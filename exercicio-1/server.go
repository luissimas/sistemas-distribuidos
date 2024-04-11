package main

import (
	"log/slog"
	"os"

	"github.com/zeromq/goczmq"
)

func main() {
	// Creating the Router (server).
	router, err := goczmq.NewRouter("tcp://*:6969")
	if err != nil {
		slog.Error("Could not create router", slog.Any("error", err))
		os.Exit(1)
	}
	// Ensure that the router will be destroyed at the end of the
	// program. This will be executed only at the end of the main
	// function.
	defer router.Destroy()

	slog.Info("Created router")

	// Receiving messages in a infinite loop.
	for {
		// Receive a message. In this case the first element of req is a
		// routing id assigned by ZeroMQ and the second element is the
		// message itself.
		req, err := router.RecvMessage()
		if err != nil {
			slog.Error("Could not receive message", slog.Any("error", err))
			os.Exit(1)
		}

		slog.Info("Received message", slog.String("msg", string(req[1])))

		// Send the first frame as req[0] to indicate the routing id
		// of the message. The flag goczmq.FlagMore signals that the
		// message contains more frames.
		err = router.SendFrame(req[0], goczmq.FlagMore)
		if err != nil {
			slog.Error("Could not send first response frame", slog.Any("error", err))
			os.Exit(1)
		}

		// Append a "*" to the message.
		resp := append(req[1], byte('*'))

		// Send the first response. The flag goczmq.FlagNone signals
		// that this is the last frame of the message.
		err = router.SendFrame(resp, goczmq.FlagNone)
		if err != nil {
			slog.Error("Could not send response", slog.Any("error", err))
			os.Exit(1)
		}

		slog.Info("Sent response", slog.String("resp", string(resp)))
	}
}
