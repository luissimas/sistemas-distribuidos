from dataclasses import dataclass
from threading import Thread

import structlog
import zmq

logger = structlog.get_logger()


class Server:
    """A pub-sub broker server."""

    def __init__(self, topic: str, pub_port: int, sub_port: int):
        self.topic = topic.encode()
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, self.topic)
        self.pub_address = f"tcp://*:{pub_port}"
        self.sub_address = f"tcp://*:{sub_port}"
        self.thread = Thread(target=self._recv_loop)

    def bind(self):
        """Bind sockets to the network interface."""
        logger.info("Binding to sockets", topic=self.topic)
        self.pub_socket.bind(self.pub_address)
        self.sub_socket.bind(self.sub_address)

    def start(self):
        """Start a background thread to receive and distribute messages."""
        logger.info("Starting server")
        self.thread.start()

    def _recv_loop(self):
        while True:
            msg = self.sub_socket.recv_multipart()
            logger.debug("Received message", msg=msg)
            self.pub_socket.send_multipart(msg)
