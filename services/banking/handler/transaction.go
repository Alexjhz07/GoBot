package handler

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/google/uuid"
)

var typesAll = map[string]bool{
	"initial":  true,
	"daily":    true,
	"weekly":   true,
	"monthly":  true,
	"transfer": true,
	"flip":     true,
	"wordle":   true,
}

var typesSingleEntry = map[string]bool{
	"initial": true,
	"daily":   true,
	"weekly":  true,
	"monthly": true,
	"flip":    true,
	"wordle":  true,
}

var typesExchange = map[string]bool{
	"transfer": true,
}

type TransactionRequest struct {
	Type      string `json:"type"`
	Amount    int64  `json:"amount"`
	Id        int64  `json:"user_id"`
	Target_Id int64  `json:"target_id,omitempty"`
}

type Transaction struct{}

func (q *Transaction) PostTransaction(w http.ResponseWriter, r *http.Request) {
	parsedRequest, err := parseRequestJSON(r)
	if err != nil {
		fmt.Println("error decoding incoming request: ", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	if typesSingleEntry[parsedRequest.Type] {
		err = handleSingleEntry(parsedRequest)
	} else if typesExchange[parsedRequest.Type] {
		err = handleExchange(parsedRequest)
	} else {
		fmt.Println("error in type handling")
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	if err != nil {
		fmt.Println("error sending request to database: ", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	w.WriteHeader(http.StatusOK)
}

// Parser, consider moving to utils area in the future
func parseRequestJSON(r *http.Request) (*TransactionRequest, error) {
	decoder := json.NewDecoder(r.Body)

	ret := &TransactionRequest{}
	err := decoder.Decode(ret)
	if err != nil {
		return nil, err
	}

	if !typesAll[ret.Type] {
		return nil, fmt.Errorf("error %q is not a valid type", ret.Type)
	}

	return ret, nil
}

func handleSingleEntry(t *TransactionRequest) error {
	groupId := uuid.New()

	queryRaw := `INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id, group_uuid) VALUES ($1, $2, $3, $4)`
	arguments := fmt.Sprintf(`[%q, %d, %d, %q]`, t.Type, t.Amount, t.Id, groupId)
	queryString := fmt.Sprintf(`{"queries": [%q], "arguments": [%s]}`, queryRaw, arguments)

	fmt.Println(queryString)
	requestBody := bytes.NewReader([]byte(queryString))

	response, err := http.Post("http://localhost:3815/api/v1/exec", "application/json", requestBody)
	if err != nil {
		return err
	}

	if response.StatusCode != http.StatusOK {
		return fmt.Errorf("status code not 200: %d", response.StatusCode)
	}

	return nil
}

func handleExchange(t *TransactionRequest) error {
	if t.Target_Id == 0 {
		return fmt.Errorf("target key cannot be empty in exchange class transaction")
	}

	groupId := uuid.New()

	queryRaw := `INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id, group_uuid) VALUES ($1, $2, $3, $4)`
	argumentsFrom := fmt.Sprintf(`[%q, %d, %d, %q]`, t.Type, -t.Amount, t.Id, groupId)
	argumentsTo := fmt.Sprintf(`[%q, %d, %d, %q]`, t.Type, t.Amount, t.Target_Id, groupId)
	queryString := fmt.Sprintf(`{"queries": [%q, %q], "arguments": [%s, %s]}`, queryRaw, queryRaw, argumentsFrom, argumentsTo)

	requestBody := bytes.NewReader([]byte(queryString))

	response, err := http.Post("http://localhost:3815/api/v1/exec", "application/json", requestBody)
	if err != nil {
		return err
	}

	if response.StatusCode != http.StatusOK {
		return fmt.Errorf("status code not 200: %d", response.StatusCode)
	}

	return nil
}
