from threading import Thread
from tkinter import (
    END,
    LEFT,
    Button,
    E,
    Entry,
    Event,
    Frame,
    Label,
    N,
    S,
    Tk,
    W,
    mainloop,
)

import structlog
from client import Client
from cv2 import COLOR_BGR2RGBA, VideoCapture, cvtColor
from PIL import Image, ImageTk

logger = structlog.get_logger()

window = Tk()

video_frame = Frame(master=window, borderwidth=1, padx=10, pady=10, bg="red")
video_frame.grid(row=0, column=0, sticky=E + W + N + S)

chat_frame = Frame(master=window, borderwidth=1, padx=10, pady=10, bg="blue")
chat_frame.grid(row=0, column=1, sticky=E + W + N + S)

window.columnconfigure(0, weight=3)
window.columnconfigure(1, weight=1)
window.rowconfigure(0, weight=1)

capture = VideoCapture(0)
camera = Label(master=video_frame)
camera.grid(row=0, column=0)


message_client = Client(topic="messages")


def send_message():
    msg = message_entry.get()
    message_entry.delete(0, END)
    message_client.send(msg)


message_list = Label(master=chat_frame, justify=LEFT)
message_entry = Entry(master=chat_frame)
message_entry.bind("<Return>", lambda _: send_message())
message_button = Button(master=chat_frame, text="Send", command=send_message)
message_list.grid(row=0, column=0, columnspan=2, sticky=N + W)
message_entry.grid(row=1, column=0, sticky=S)
message_button.grid(row=1, column=1, sticky=S)


def capture_video():
    _, frame = capture.read()
    img = cvtColor(frame, COLOR_BGR2RGBA)
    # logger.debug("Capturing video frame")
    # TODO: send img to socket
    imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
    camera.imgtk = imgtk
    camera.configure(image=imgtk)
    camera.after(10, capture_video)


def recv_loop():
    while True:
        user, msg = message_client.recv()
        message_list["text"] += f"{user}: {msg}\n"


def handle_keypress(event: Event):
    logger.debug("Handled keypress", tkevent=event)


def handle_click(event: Event):
    logger.debug("Handled click", tkevent=event)


# window.bind("<Key>", handle_keypress)
window.bind("<Button-1>", handle_click)
camera.bind("<Button-1>", lambda e: logger.debug("Handled camera click", tkevent=e))

if __name__ == "__main__":
    Thread(target=recv_loop).start()
    message_client.connect()
    capture_video()
    mainloop()
