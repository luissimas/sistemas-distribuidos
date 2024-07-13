import logging
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from queue import Queue
from time import time
from typing import Callable, Dict, Tuple

import structlog
from PIL import Image, ImageTk

from trabalho_1.client import Client, Message
from trabalho_1.video_capture import VideoCapture

structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.INFO))
logger = structlog.get_logger(__name__)


@dataclass
class User:
    last_seen: datetime
    video_label: tk.Label


class Video(tk.Frame):
    """The video display user interface."""

    def __init__(self, master: tk.Tk, video_queue: Queue[Tuple[str, Image.Image]]):
        super().__init__(master=master, borderwidth=1, padx=10, pady=10)
        self.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        self.video_queue = video_queue
        self.users: Dict[str, User] = {}
        self.display_videos()
        self.user_inactivity_threshold = 2

    def display_videos(self):
        while not self.video_queue.empty():
            name, image = self.video_queue.get()
            user = self.users.get(name)
            if user is None:
                user = User(last_seen=datetime.now(), video_label=tk.Label(master=self))
                self.users[name] = user
            else:
                user.last_seen = datetime.now()
            self._display_image(self.users[name].video_label, image)
        self._clear_inactive()
        self._draw_grid()
        self.master.after(30, self.display_videos)

    def _clear_inactive(self):
        active_users = {}
        for name, user in self.users.items():
            if (
                datetime.now() - user.last_seen
            ).seconds >= self.user_inactivity_threshold:
                logger.info("Removing inactive user", user=name)
                user.video_label.grid_forget()
            else:
                active_users[name] = user

        self.users = active_users
        self._draw_grid()

    def _draw_grid(self):
        self.pack_forget()
        row = 0
        column = 0
        size = len(self.users) // 2
        for user in self.users.values():
            user.video_label.grid(row=row, column=column)
            if column > size:
                column = 0
                row += 1
            else:
                column += 1

    def _display_image(self, label: tk.Label, image: Image.Image):
        label.image = ImageTk.PhotoImage(image)
        label.configure(image=label.image)


class Chat(tk.Frame):
    """The chat user interface."""

    def __init__(self, master: tk.Tk, send_message: Callable[[str], None]):
        super().__init__(master=master, borderwidth=1, padx=10, pady=10)
        super().grid(row=0, column=1, sticky=tk.E + tk.W + tk.N + tk.S)
        self.message_list = tk.Label(master=self, justify=tk.LEFT, wraplength=300)
        self.message_entry = tk.Entry(master=self)
        self.message_entry.bind(
            "<Return>", lambda _: self._handle_message_entry_submit()
        )
        self.message_button = tk.Button(
            master=self, text="Send", command=self._handle_message_entry_submit
        )
        self.message_list.grid(row=0, column=0, columnspan=2, sticky=tk.N + tk.W)
        self.message_entry.grid(row=1, column=0, sticky=tk.S)
        self.message_button.grid(row=1, column=1, sticky=tk.S)
        self.send_message = send_message

    def append_message(self, msg: Message):
        """Appends a new message to the chat."""
        self.message_list["text"] += f"{msg.sender}: {msg.content.decode()}\n"

    def _handle_message_entry_submit(self):
        contents = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        self.send_message(contents)


class Application:
    """The main application."""

    def __init__(self, broker_address: str, username: str):
        self.root = tk.Tk()
        self.username = username
        # Clients to comunicate with the broker
        self.broker_address = broker_address
        self.text_client = Client(
            broker_address=broker_address,
            topic="text",
            sub_port=4000,
            pub_port=4001,
            on_message_received=self._handle_received_message,
        )
        self.video_client = Client(
            broker_address=broker_address,
            topic="video",
            sub_port=4002,
            pub_port=4003,
            on_message_received=self._handle_received_video,
        )

        # Video capture device
        self.video_capture = VideoCapture(on_frame_captured=self._handle_frame_captured)
        self.video_queue: Queue[Tuple[str, Image.Image]] = Queue()

        # Application UI components
        self.chat = Chat(self.root, send_message=self._handle_send_message)
        self.video = Video(self.root, video_queue=self.video_queue)

        # Application layout
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

    def start(self):
        """Start the application main loop."""
        logger.info(
            "Starting the main application.", broker_address=self.broker_address
        )
        self.text_client.connect()
        self.video_client.connect()
        self.text_client.start_receiving()
        self.video_client.start_receiving()
        self.video_capture.start_capturing()
        self.root.mainloop()

    def _handle_received_message(self, msg: Message):
        self.chat.append_message(msg)

    def _handle_received_video(self, msg: Message):
        stream = BytesIO(msg.content)
        image = Image.open(stream)
        self.video_queue.put((msg.sender, image))

    def _handle_frame_captured(self, frame: Image.Image):
        image = BytesIO()
        # TODO: use a more appropriate format
        frame.save(image, format="PNG")
        msg = Message(sender=self.username, content=image.getvalue())
        self.video_client.send(msg)

    def _handle_send_message(self, content: str):
        msg = Message(sender=self.username, content=content.encode())
        self.text_client.send(msg)
