package application

import (
	"context"
	"database/sql"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"time"

	_ "github.com/lib/pq"
)

type DatabaseApp struct {
	router http.Handler
	db     *sql.DB
}

func New() (*DatabaseApp, error) {
	app := &DatabaseApp{}

	if err := app.loadDatabase(); err != nil {
		return nil, err
	}

	app.loadRoutes()

	return app, nil
}

func (a *DatabaseApp) loadDatabase() error {
	port, err := strconv.Atoi(os.Getenv("DB_PORT"))
	if err != nil {
		panic(err)
	}

	fmt.Println(os.Getenv("DB_USER"))

	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s dbname=%s password=%s sslmode=disable",
		os.Getenv("DB_HOST"),
		port,
		os.Getenv("DB_USER"),
		os.Getenv("DB_NAME"),
		os.Getenv("DB_PASS"),
	)

	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		return fmt.Errorf("failed to open database connection")
	}

	err = db.Ping()
	if err != nil {
		return fmt.Errorf("failed during database ping")
	}

	a.db = db

	return nil
}

func (a *DatabaseApp) Start(ctx context.Context) error {
	server := http.Server{
		Addr:    ":3815",
		Handler: a.router,
	}

	defer func() {
		if err := a.db.Close(); err != nil {
			fmt.Println("failed to close database connection: ", err)
		} else {
			fmt.Println("database connnection closed successfully")
		}
	}()

	ch := make(chan error, 1)

	go func() {
		err := server.ListenAndServe()
		if err != nil {
			ch <- fmt.Errorf("failed to start database server: %w", err)
		}
		close(ch)
	}()

	fmt.Println("[service] database up success")

	select {
	case err := <-ch:
		return err
	case <-ctx.Done():
		timeout, cancel := context.WithTimeout(context.Background(), time.Second*10)
		defer cancel()

		return server.Shutdown(timeout)
	}
}
