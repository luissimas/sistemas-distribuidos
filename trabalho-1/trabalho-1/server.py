import zmq
import structlog

logger = structlog.get_logger()
context = zmq.Context()
topic = b"messages"

logger.info("Binding to sockets")

pub_socket = context.socket(zmq.PUB)
sub_socket = context.socket(zmq.SUB)
pub_socket.bind("tcp://*:4000")
sub_socket.bind("tcp://*:4001")
sub_socket.setsockopt(zmq.SUBSCRIBE, topic)

while True:
    msg = sub_socket.recv_multipart()
    logger.debug("Received message", msg=msg)
    pub_socket.send_multipart(msg)
