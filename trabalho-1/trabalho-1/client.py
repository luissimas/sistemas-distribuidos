import zmq
import structlog
from threading import Thread

logger = structlog.get_logger()
context = zmq.Context()

logger.info("Connecting to broker")

pub_socket = context.socket(zmq.PUB)
sub_socket = context.socket(zmq.SUB)
pub_socket.connect("tcp://localhost:4001")
sub_socket.connect("tcp://localhost:4000")

logger.info("Connected to broker")

topic = input("Topic: ").encode()
username = input("Username: ")

sub_socket.setsockopt(zmq.SUBSCRIBE, topic)

def recv():
    while True:
        msg = sub_socket.recv_multipart()
        logger.info("Received message", msg=msg)

def send():
    while True:
        msg = input("> ")
        pub_socket.send_multipart([topic, f"{username}: {msg}".encode()])


recv_thread = Thread(target=recv)
pub_thread = Thread(target=send)

recv_thread.start()
pub_thread.start()

recv_thread.join()
pub_thread.join()
