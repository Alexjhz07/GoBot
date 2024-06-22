package handler

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type ExperienceRequest struct {
	Id    int64 `json:"user_id"`
	Delta int64 `json:"delta"`
}

type Experience struct{}

func (q *Experience) ModifyExperience(w http.ResponseWriter, r *http.Request) {
	parsedRequest, err := parseRequestJSON(r)
	if err != nil {
		fmt.Println("error decoding incoming request: ", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	query := `UPDATE user_experience SET experience = experience + $1 WHERE user_id = $2`
	arguments := fmt.Sprintf(`[%d, %d]`, parsedRequest.Delta, parsedRequest.Id)
	queryString := fmt.Sprintf(`{"queries": [%q], "arguments": [%s]}`, query, arguments)

	requestBody := bytes.NewReader([]byte(queryString))

	response, err := http.Post("http://localhost:3815/api/v1/exec", "application/json", requestBody)
	if err != nil {
		fmt.Println("error sending request to database: ", err)
		w.WriteHeader(http.StatusServiceUnavailable)
		return
	}

	if response.StatusCode != http.StatusOK {
		fmt.Println("status code not 200: ", response.StatusCode)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// Parser, consider moving to utils area in the future
func parseRequestJSON(r *http.Request) (*ExperienceRequest, error) {
	decoder := json.NewDecoder(r.Body)

	ret := &ExperienceRequest{}
	err := decoder.Decode(ret)
	if err != nil {
		return nil, err
	}

	return ret, nil
}
