from dataclasses import dataclass
from enum import StrEnum
from threading import Thread
from typing import Callable

import structlog
import zmq

logger = structlog.get_logger(__name__)


class MessageType(StrEnum):
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"


@dataclass
class Message:
    type: MessageType
    sender: str
    content: bytes


class Client:
    """A threaded pub-sub client."""

    def __init__(
        self,
        broker_address: str,
        topic: str,
        on_message_received: Callable[[Message], None],
    ):
        self.context = zmq.Context()
        self.topic = topic.encode()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, self.topic)
        self.broker_address = broker_address
        self.on_message_received = on_message_received
        self.thread = Thread(target=self._recv_loop)

    def connect(self):
        """Connects the client to the broker."""
        logger.info("Connecting to broker", broker_address=self.broker_address)
        self.pub_socket.connect(f"tcp://{self.broker_address}:4001")
        self.sub_socket.connect(f"tcp://{self.broker_address}:4000")
        logger.info("Connected to broker")

    def start_receiving(self):
        """Starts a background thread to receive messages."""
        self.thread.start()

    def send(self, msg: Message):
        """Send `msg` to the broker."""
        full_msg = [self.topic, msg.sender.encode(), msg.type.encode(), msg.content]
        self.pub_socket.send_multipart(full_msg)
        logger.debug("Sent message", msg=full_msg)

    def _recv_loop(self):
        while True:
            raw_msg = self.sub_socket.recv_multipart()
            sender = raw_msg[1].decode()
            msg_type = MessageType(raw_msg[2].decode())
            content = raw_msg[3]
            msg = Message(type=msg_type, sender=sender, content=content)
            logger.info("Received message", msg=msg)
            self.on_message_received(msg)
