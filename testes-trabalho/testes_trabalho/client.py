import logging
import random
import time
from threading import Thread

import zmq

logging.basicConfig(encoding="utf-8", level=logging.DEBUG)
logger = logging.getLogger(__name__)

context = zmq.Context()

logger.info("Connecting to broker…")

pub_socket = context.socket(zmq.PUB)
sub_socket = context.socket(zmq.SUB)
pub_socket.connect("tcp://localhost:4000")
sub_socket.connect("tcp://localhost:4001")

logger.info("Connected to broker!")

name = input("Username: ")
topic = input("Topic: ")

sub_socket.setsockopt(zmq.SUBSCRIBE, topic.encode())


def recv():
    while True:
        msg = sub_socket.recv_multipart()
        logger.info("Received msg %s", msg)


def publish():
    while True:
        msg = input("> ")
        time.sleep(random.random())
        logger.info("Sending msg %s", msg)
        pub_socket.send_multipart([topic.encode(), (f"{name}: {msg}").encode()])


recv_thread = Thread(target=recv)
pub_thread = Thread(target=publish)

recv_thread.start()
pub_thread.start()

recv_thread.join()
pub_thread.join()
