package handler

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
)

type DatabaseRequest struct {
	Query     []string `json:"queries"`
	Arguments [][]any  `json:"arguments,omitempty"`
}

type Database struct {
	Database *sql.DB
}

type DatabaseResponse struct {
	Responses [][]any `json:"responses,omitempty"`
}

// Takes in an http request and parses it into a DatabaseRequest
// Returns decoding error or argument length error if they occur
func parseRequestJSON(r *http.Request) (*DatabaseRequest, error) {
	decoder := json.NewDecoder(r.Body)
	decoder.UseNumber()

	ret := &DatabaseRequest{}
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
