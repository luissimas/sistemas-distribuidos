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

	slog.Info("Created router")

	for {

		req, err := router.RecvMessage()
		if err != nil {
			slog.Error("Could not receive message", slog.Any("error", err))
			os.Exit(1)
		}

		slog.Info("Received message", slog.String("msg", string(req[1])))

		err = router.SendFrame(req[0], goczmq.FlagMore)
		if err != nil {
			slog.Error("Could not send first response frame", slog.Any("error", err))
			os.Exit(1)
		}

		resp := append(req[1], byte('*'))

		err = router.SendFrame(resp, goczmq.FlagNone)
		if err != nil {
			slog.Error("Could not send response", slog.Any("error", err))
			os.Exit(1)
		}

		slog.Info("Sent message")
	}
}
