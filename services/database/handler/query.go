package handler

import (
	"database/sql"
	"net/http"
)

type Query struct {
	Database *sql.DB
}

func (q *Query) AnyQuery(w http.ResponseWriter, r *http.Request) {
}
