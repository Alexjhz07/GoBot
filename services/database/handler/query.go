package handler

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
)

type QueryRequest struct {
	Query     []string `json:"queries"`
	Arguments [][]any  `json:"arguments,omitempty"`
}

type Query struct {
	Database *sql.DB
}

func (q *Query) SimpleExec(w http.ResponseWriter, r *http.Request) {
	parsedRequest, err := parseRequestJSON(r)
	if err != nil {
		fmt.Println("error decoding incoming request: ", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	tx, err := q.Database.Begin()
	if err != nil {
		fmt.Println("error starting transaction")
		return
	}

	defer tx.Rollback()

	for i := 0; i < len(parsedRequest.Query); i++ {
		fmt.Println(parsedRequest.Query[i])
		fmt.Println(parsedRequest.Arguments[i]...)
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

// Parser, consider moving to utils area in the future
func parseRequestJSON(r *http.Request) (*QueryRequest, error) {
	decoder := json.NewDecoder(r.Body)

	ret := &QueryRequest{}
	err := decoder.Decode(ret)
	if err != nil {
		return nil, err
	}

	if len(ret.Query) == 0 {
		return nil, fmt.Errorf("length of query is 0")
	}

	if len(ret.Query) != len(ret.Arguments) {
		return nil, fmt.Errorf("length mismatch between query and argument expected %d received %d", len(ret.Query), len(ret.Arguments))
	}

	return ret, nil
}
