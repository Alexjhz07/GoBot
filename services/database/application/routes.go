package application

import (
	"Alexjhz07/GoBot/services/database/handler"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

func loadRoutes() *chi.Mux {
	router := chi.NewRouter()

	router.Use(middleware.Logger)

	router.Route("/query", loadQueryRoutes)

	return router
}

func loadQueryRoutes(router chi.Router) {
	queryHandler := &handler.Query{}

	router.Post("/", queryHandler.AnyQuery)
}
