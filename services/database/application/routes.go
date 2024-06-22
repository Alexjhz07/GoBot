package application

import (
	"Alexjhz07/GoBot/services/database/handler"
	"fmt"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

func (a *DatabaseApp) loadRoutes() {
	router := chi.NewRouter()

	router.Use(middleware.Logger)

	router.Route("/api/v1", a.loadV1Routes)

	a.router = router
}

func (a *DatabaseApp) loadV1Routes(router chi.Router) {
	execHandler := &handler.Exec{
		Database: a.db,
	}

	router.Post("/exec", execHandler.SimpleExec)
	fmt.Println("Loaded query routes")
}
