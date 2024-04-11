package main

import (
	"log/slog"
	"os"

	"github.com/zeromq/goczmq"
)

func main() {
	router, err := goczmq.NewRouter("tcp://*:6969")
	if err != nil {
		slog.Error("Could not create router", slog.Any("error", err))
		os.Exit(1)
	}
	defer router.Destroy()

	dealer, err := goczmq.NewDealer("tcp://127.0.0.1:6969")
	if err != nil {
		slog.Error("Could not create dealer", slog.Any("error", err))
		os.Exit(1)
	}

	err = dealer.SendFrame([]byte("Hello"), goczmq.FlagNone)
	if err != nil {
		slog.Error("Could not send frame", slog.Any("error", err))
		os.Exit(1)
	}

	req, err := router.RecvMessage()
	if err != nil {
		slog.Error("Could not receive message", slog.Any("error", err))
		os.Exit(1)
	}

	slog.Info("Received message", slog.String("from", string(req[0])), slog.String("msg", string(req[1])))

	err = router.SendFrame(req[0], goczmq.FlagMore)
	if err != nil {
		slog.Error("Could not send first response frame", slog.Any("error", err))
		os.Exit(1)
	}

	err = router.SendFrame([]byte("World"), goczmq.FlagMore)
	if err != nil {
		slog.Error("Could not send response", slog.Any("error", err))
		os.Exit(1)
	}

	slog.Info("Created router")
}
