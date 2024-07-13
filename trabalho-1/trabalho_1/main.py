from getpass import getuser
from threading import Thread
from typing import Annotated, List

import structlog
from typer import Option, Typer

from trabalho_1.application import Application
from trabalho_1.server import Server

app = Typer()

logger = structlog.get_logger(__name__)


@app.command(help="Run the client GUI application.")
def client(
    broker_address: Annotated[
        str, Option(help="The IP address or hostname of the message broker.")
    ] = "127.0.0.1",
    username: Annotated[
        str, Option(help="The username to use on the room.")
    ] = getuser(),
):
    application = Application(broker_address=broker_address, username=username)
    application.start()


@app.command(help="Run the message broker server.")
def server():
    threads: List[Thread] = []
    server_spec = [
        ("text", 4000, 4001),
        ("video", 4002, 4003),
        ("audio", 4004, 4005),
    ]
    for topic, pub_port, sub_port in server_spec:
        logger.info(
            "Starting server", topic=topic, pub_port=pub_port, sub_port=sub_port
        )
        server = Server(topic=topic, pub_port=pub_port, sub_port=sub_port)
        server.bind()
        server.start()
        threads.append(server.thread)

    for thread in threads:
        thread.join()
