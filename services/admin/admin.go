package main

import (
	"fmt"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

func main() {
	router := chi.NewRouter()
	router.Use(middleware.CleanPath)
	router.Use(middleware.Logger)

	router.Get("/ping", pingGet)

	server := &http.Server{
		Addr:    ":3080",
		Handler: router,
	}

	err := server.ListenAndServe()
	if err != nil {
		fmt.Println("Failed to Listen to Admin Server")

	}
}

func pingGet(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("pong"))
}
