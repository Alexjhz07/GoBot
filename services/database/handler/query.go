package handler

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
)

type QueryRequest struct {
	Query     string `json:"query"`
	Arguments []any  `json:"arguments,omitempty"`
}

type Query struct {
	Database *sql.DB
}

func (q *Query) AnyQuery(w http.ResponseWriter, r *http.Request) {
	parsedRequest, err := parseRequestJSON(r)
	if err != nil {
		fmt.Println("error decoding incoming request: ", err)
		w.WriteHeader(400)
		return
	}

	_, err = q.Database.Exec(parsedRequest.Query, parsedRequest.Arguments...)
	if err != nil {
		fmt.Println("error executing statement: ", err)
		w.WriteHeader(400)
	} else {
		w.WriteHeader(200)
	}
}

// Parser, consider moving to utils area in the future
func parseRequestJSON(r *http.Request) (*QueryRequest, error) {
	decoder := json.NewDecoder(r.Body)

	ret := &QueryRequest{}
	err := decoder.Decode(ret)
	if err != nil {
		return nil, err
	}

	return ret, nil
}
