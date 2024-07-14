package application

import (
	"Alexjhz07/GoBot/services/banking/handler"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

func (a *App) loadRoutes() {
	router := chi.NewRouter()

	router.Use(middleware.Logger)

	router.Route("/api/v1", a.loadBankingRoutes)

	a.router = router
}

func (a *App) loadBankingRoutes(router chi.Router) {
	transactionHandler := &handler.Transaction{}
	accountHandler := &handler.Account{}

	router.Post("/transaction", transactionHandler.PostTransaction)
	router.Post("/account", accountHandler.PostAccount)
}
