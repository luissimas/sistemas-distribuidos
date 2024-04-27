import cv2

vid = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
filename = "video.mp4"
fps = 20.0
shape = (640, 480)

writer = cv2.VideoWriter(filename, fourcc, fps, shape)

print("Started capturing")
try:
    while True:
        ok, frame = vid.read()
        writer.write(frame)
except KeyboardInterrupt:
    ...

print("Done")
vid.release()
writer.release()
