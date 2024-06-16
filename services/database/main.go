package main

import (
	"Alexjhz07/GoBot/services/database/application"
	"context"
	"fmt"
	"os"
	"os/signal"
)

func main() {
	app, err := application.New()
	if err != nil {
		fmt.Println("failed to create application")
		return
	}

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	err = app.Start(ctx)
	if err != nil {
		fmt.Println("failed to start database app", err)
	}
}
