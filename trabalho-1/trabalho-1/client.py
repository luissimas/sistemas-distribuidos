from getpass import getuser
from typing import Tuple
import zmq
import structlog

logger = structlog.get_logger(__name__)


class Client:
    def __init__(self, topic: str):
        self.context = zmq.Context()
        self.topic = topic.encode()
        self.username = getuser()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, self.topic)

    def connect(self):
        logger.info("Connecting to broker")
        self.pub_socket.connect("tcp://localhost:4001")
        self.sub_socket.connect("tcp://localhost:4000")
        logger.info("Connected to broker")

    def recv(self) -> Tuple[str, str]:
        msg = self.sub_socket.recv_multipart()
        logger.info("Received message", msg=msg)
        return msg[1].decode(), msg[2].decode()

    def send(self, msg: str):
        full_msg = [self.topic, self.username.encode(), msg.encode()]
        self.pub_socket.send_multipart(full_msg)
        logger.debug("Sent message", msg=full_msg)
