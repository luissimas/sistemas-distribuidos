from sys import argv

from application import Application

if __name__ == "__main__":
    if len(argv) < 2:
        print(f"Usage:\n\tpython {argv[0]} <broker-address>")
        exit(1)
    application = Application(broker_address=argv[1])
    application.start()
