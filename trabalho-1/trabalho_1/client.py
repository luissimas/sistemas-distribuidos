from dataclasses import dataclass
from enum import StrEnum
from threading import Thread
from typing import Callable

import structlog
import zmq

logger = structlog.get_logger(__name__)


@dataclass
class Message:
    sender: str
    content: bytes


class Client:
    """A threaded pub-sub client."""

    def __init__(
        self,
        broker_address: str,
        pub_port: int,
        sub_port: int,
        topic: str,
        on_message_received: Callable[[Message], None],
    ):
        self.context = zmq.Context()
        self.topic = topic.encode()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, self.topic)
        self.pub_address = f"tcp://{broker_address}:{pub_port}"
        self.sub_address = f"tcp://{broker_address}:{sub_port}"
        self.on_message_received = on_message_received
        self.thread = Thread(target=self._recv_loop, daemon=True)

    def connect(self):
        """Connects the client to the broker."""
        logger.info(
            "Connecting to broker",
            pub_address=self.pub_address,
            sub_address=self.sub_address,
        )
        self.pub_socket.connect(self.pub_address)
        self.sub_socket.connect(self.sub_address)
        logger.info("Connected to broker")

    def start_receiving(self):
        """Starts a background thread to receive messages."""
        self.thread.start()

    def send(self, msg: Message):
        """Send `msg` to the broker."""
        full_msg = [self.topic, msg.sender.encode(), msg.content]
        self.pub_socket.send_multipart(full_msg)
        logger.debug("Sent message", msg=full_msg)

    def _recv_loop(self):
        while True:
            raw_msg = self.sub_socket.recv_multipart()
            sender = raw_msg[1].decode()
            content = raw_msg[2]
            msg = Message(sender=sender, content=content)
            logger.debug("Received message", msg=msg)
            self.on_message_received(msg)
