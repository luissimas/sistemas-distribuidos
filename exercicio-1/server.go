package main

import (
	"context"
	"log/slog"
	"os"
	"time"

	zmq "github.com/go-zeromq/zmq4"
)

func main() {
	// Creating the Router (server).
	router := zmq.NewRouter(context.Background())
	err := router.Listen("tcp://*:6969")
	if err != nil {
		slog.Error("Could not create router", slog.Any("error", err))
		os.Exit(1)
	}
	// Ensure that the router will be closed at the end of the
	// program. This will be executed only at the end of the main
	// function.
	defer router.Close()

	slog.Info("Created router")
	durations := []time.Duration{}
	var average time.Duration

	// Receiving messages in a infinite loop.
	for {
		// Receive a message. In this case the first element of req is a
		// routing id assigned by ZeroMQ and the second element is the
		// message itself.
		req, err := router.Recv()
		start := time.Now()
		if err != nil {
			slog.Error("Could not receive message", slog.Any("error", err))
			os.Exit(1)
		}

		msg := req.String()
		slog.Info("Received message", slog.String("msg", msg))

		// Send the first frame as req[0] to indicate the routing id
		// of the message. The flag goczmq.FlagMore signals that the
		// message contains more frames.
		respText := append(req.Frames[1], byte('*'))
		resp := zmq.NewMsgFrom(req.Frames[0], respText)
		err = router.Send(resp)
		duration := time.Since(start)
		if err != nil {
			slog.Error("Could not send response", slog.Any("error", err))
			os.Exit(1)
		}

		durations = append(durations, duration)
		average = average + ((duration - average) / time.Duration(len(durations)))
		slog.Info("Sent response", slog.String("resp", string(respText)), slog.Duration("processing_time", duration), slog.Duration("average", average))
	}
}
