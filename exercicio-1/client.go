package main

import (
	"log/slog"
	"os"

	"github.com/zeromq/goczmq"
)

func main() {
	// Creating the Dealer (client).
	dealer, err := goczmq.NewDealer("tcp://127.0.0.1:6969")
	if err != nil {
		slog.Error("Could not create dealer", slog.Any("error", err))
		os.Exit(1)
	}

	slog.Info("Created dealer")

	// Sending the message.
	err = dealer.SendFrame([]byte("Hello"), goczmq.FlagNone)
	if err != nil {
		slog.Error("Could not send frame", slog.Any("error", err))
		os.Exit(1)
	}

	slog.Info("Sent message")

	// Receiving the response.
	resp, err := dealer.RecvMessage()
	if err != nil {
		slog.Error("Could not receive message", slog.Any("error", err))
		os.Exit(1)
	}

	slog.Info("Received message", slog.String("msg", string(resp[0])))
}
