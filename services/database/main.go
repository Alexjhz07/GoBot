package main

import (
	"Alexjhz07/GoBot/services/database/application"
	"context"
	"fmt"
	"os"
	"os/signal"

	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load(".env")

	if err != nil {
		fmt.Println("Error loading .env file")
		return
	}

	app, err := application.New()
	if err != nil {
		fmt.Println("failed to create application:", err)
		return
	}

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt)
	defer cancel()

	err = app.Start(ctx)
	if err != nil {
		fmt.Println("failed to start database app", err)
	}
}
