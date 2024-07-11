from typing import Annotated

from typer import Option, Typer

from trabalho_1.application import Application
from trabalho_1.server import Server

app = Typer()

topic = "room"


@app.command(help="Run the client GUI application.")
def client(
    broker_address: Annotated[
        str, Option(help="The IP address or hostname of the message broker.")
    ] = "127.0.0.1"
):
    application = Application(broker_address=broker_address, topic=topic)
    application.start()


@app.command(help="Run the message broker server.")
def server():
    server = Server(topic=topic)
    server.bind()
    server.start()
