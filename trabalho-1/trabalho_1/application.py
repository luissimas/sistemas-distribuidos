import tkinter as tk
from getpass import getuser
from typing import Callable

import structlog
from PIL import ImageTk

from trabalho_1.client import Client, Message, MessageType
from trabalho_1.video_capture import VideoCapture

logger = structlog.get_logger(__name__)


class Video(tk.Frame):
    """The video display user interface."""

    def __init__(self, master: tk.Tk):
        super().__init__(master=master, borderwidth=1, padx=10, pady=10, bg="red")
        self.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)
        self.camera = tk.Label(master=self)
        self.camera.grid(row=0, column=0)
        self.capture = VideoCapture()
        self.capture_video()

    # TODO: instead of capturing video directly, display streams from
    # zeromq sockets
    def capture_video(self):
        image = self.capture.capture_frame()
        image = ImageTk.PhotoImage(image)
        self.camera.image = image
        self.camera.configure(image=image)
        self.camera.after(10, self.capture_video)


class Chat(tk.Frame):
    """The chat user interface."""

    def __init__(self, master: tk.Tk, send_message: Callable[[str], None]):
        super().__init__(master=master, borderwidth=1, padx=10, pady=10, bg="blue")
        super().grid(row=0, column=1, sticky=tk.E + tk.W + tk.N + tk.S)
        self.message_list = tk.Label(master=self, justify=tk.LEFT)
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

    def __init__(self, broker_address: str, topic: str):
        self.root = tk.Tk()
        self.username = getuser()
        self.broker_address = broker_address
        self.client = Client(
            broker_address=broker_address,
            topic=topic,
            on_message_received=self._handle_received_message,
        )

        # Application UI components
        self.chat = Chat(self.root, send_message=self._handle_send_message)
        self.video = Video(self.root)

        # Application layout
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

    def start(self):
        """Start the application main loop."""
        logger.info(
            "Starting the main application.", broker_address=self.broker_address
        )
        self.client.connect()
        self.client.start_receiving()
        self.root.mainloop()

    def _handle_received_message(self, msg: Message):
        self.chat.append_message(msg)

    def _handle_send_message(self, content: str):
        msg = Message(
            type=MessageType.TEXT, sender=self.username, content=content.encode()
        )
        self.client.send(msg)
