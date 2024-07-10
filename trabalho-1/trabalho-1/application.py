import tkinter as tk
from os import sendfile
from typing import Callable

import structlog
from client import Client, Message

logger = structlog.get_logger(__name__)


class Chat(tk.Frame):
    def __init__(self, master: tk.Tk, send_message: Callable[[bytes], None]):
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
        self.send_message(contents.encode())


class Application:
    def __init__(self, broker_address: str):
        self.root = tk.Tk()
        self.broker_address = broker_address
        self.message_client = Client(
            broker_address=broker_address,
            topic="room",
            on_message_received=self._handle_received_message,
        )
        self.chat = Chat(self.root, send_message=self.message_client.publish)

    def start(self):
        logger.info(
            "Starting the main application.", broker_address=self.broker_address
        )
        self.message_client.connect()
        self.message_client.start_receiving()
        self.root.mainloop()

    def _handle_received_message(self, msg: Message):
        self.chat.append_message(msg)
