package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
)

func (db *Database) SimpleQuery(w http.ResponseWriter, r *http.Request) {
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

	responses := DatabaseResponse{}

	for i := 0; i < len(parsedRequest.Query); i++ {
		rows, err := tx.Query(parsedRequest.Query[i], parsedRequest.Arguments[i]...)
		if err != nil {
			fmt.Println("error executing statement: ", err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		defer rows.Close()

		column_names, err := rows.Columns()
		if err != nil {
			fmt.Println("error fetching columns: ", err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		// Dynamically create row buffer for our query
		row_buffer := make([]string, len(column_names))
		row_buffer_ptr := make([]interface{}, len(column_names))
		for i := range len(column_names) {
			row_buffer_ptr[i] = &row_buffer[i]
		}

		response := []interface{}{}
		for rows.Next() {
			if err := rows.Scan(row_buffer_ptr...); err != nil {
				fmt.Println("error scanning rows: ", err)
			}

			row := map[string]interface{}{}
			for i, column_name := range column_names {
				row[column_name] = row_buffer[i]
			}

			response = append(response, row)
		}

		responses.Responses = append(responses.Responses, response)
	}

	json_response, err := json.Marshal(responses)
	if err != nil {
		fmt.Println("error marshalling json: ", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	tx.Commit()
	w.WriteHeader(http.StatusOK)
	w.Write(json_response)
}
