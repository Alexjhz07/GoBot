package handler

import (
	"fmt"
	"net/http"
)

func (db *Database) SimpleExec(w http.ResponseWriter, r *http.Request) {
	parsedRequest, err := parseRequestJSON(r)
	if err != nil {
		fmt.Println("error decoding incoming request: ", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	tx, err := db.Database.Begin()
	if err != nil {
		fmt.Println("error starting transaction")
		return
	}

	defer tx.Rollback()

	for i := 0; i < len(parsedRequest.Query); i++ {
		_, err = tx.Exec(parsedRequest.Query[i], parsedRequest.Arguments[i]...)
		if err != nil {
			fmt.Println("error executing statement: ", err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
	}

	tx.Commit()
	w.WriteHeader(http.StatusOK)
}
