package application

import (
	"Alexjhz07/GoBot/services/experience/handler"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

func (a *App) loadRoutes() {
	router := chi.NewRouter()

	router.Use(middleware.Logger)

	router.Route("/api/v1", a.loadExperienceRoutes)

	a.router = router
}

func (a *App) loadExperienceRoutes(router chi.Router) {
	experienceHandler := &handler.Experience{}

	router.Patch("/experience", experienceHandler.ModifyExperience)
}
