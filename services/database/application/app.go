package application

import (
	"context"
	"database/sql"
	"fmt"
	"net/http"
	"time"

	_ "github.com/lib/pq"
)

const (
	host   = "localhost"
	port   = 5434
	user   = "postgres"
	dbname = "postgres"
)

type DatabaseApp struct {
	router http.Handler
	db     *sql.DB
}

func New() *DatabaseApp {
	app := &DatabaseApp{
		router: loadRoutes(),
	}

	return app
}

func (a *DatabaseApp) Start(ctx context.Context) error {
	server := http.Server{
		Addr:    ":3815",
		Handler: a.router,
	}

	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s "+"dbname=%s sslmode=disable", host, port, user, dbname)

	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		return fmt.Errorf("failed to open database connection")
	}
	defer func() {
		if err := db.Close(); err != nil {
			fmt.Println("failed to close database connection: ", err)
		} else {
			fmt.Println("database connnection closed successfully")
		}
	}()

	err = db.Ping()
	if err != nil {
		return fmt.Errorf("failed during database ping")
	}

	a.db = db

	ch := make(chan error, 1)

	go func() {
		err = server.ListenAndServe()
		if err != nil {
			ch <- fmt.Errorf("failed to start database server: %w", err)
		}
		close(ch)
	}()

	fmt.Println("[service] database up success")

	select {
	case err = <-ch:
		return err
	case <-ctx.Done():
		timeout, cancel := context.WithTimeout(context.Background(), time.Second*10)
		defer cancel()

		return server.Shutdown(timeout)
	}
}
