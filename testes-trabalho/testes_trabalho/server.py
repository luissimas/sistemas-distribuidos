import logging

import zmq

logging.basicConfig(encoding="utf-8", level=logging.DEBUG)
logger = logging.getLogger(__name__)

context = zmq.Context()
topic = b"messages"

logger.info("Binding to sockets")

pub_socket = context.socket(zmq.PUB)
sub_socket = context.socket(zmq.SUB)
sub_socket.bind("tcp://*:4000")
pub_socket.bind("tcp://*:4001")
sub_socket.setsockopt(zmq.SUBSCRIBE, topic)

logger.info("Bound sockets!")


# The broker just publishes everything it receives
while True:
    msg = sub_socket.recv_multipart()
    logger.info("Received msg %s", msg)
    pub_socket.send_multipart(msg)
