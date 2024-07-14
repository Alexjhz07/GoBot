package handler

import (
	"bytes"
	"fmt"
	"net/http"

	"github.com/google/uuid"
)

type TransactionRequest struct {
	Type   string `json:"type"`
	Amount int64  `json:"amount"`
	Origin int64  `json:"origin_id"`
	Target int64  `json:"target_id,omitempty"`
}

type Transaction struct{}

func (t *Transaction) PostTransaction(w http.ResponseWriter, r *http.Request) {
	parsedRequest, err := parseTransactionRequestJSON(r)
	if err != nil {
		fmt.Println("error decoding incoming request: ", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	if transactionTypesSingle[parsedRequest.Type] {
		err = handleSingleEntry(parsedRequest)
	} else if transactionTypesExchange[parsedRequest.Type] {
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

func handleSingleEntry(t *TransactionRequest) error {
	groupId := uuid.New()

	queryRaw := `INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id, group_uuid) VALUES ($1, $2, $3, $4)`
	arguments := fmt.Sprintf(`[%q, %d, %d, %q]`, t.Type, t.Amount, t.Origin, groupId)
	queryString := fmt.Sprintf(`{"queries": [%q], "arguments": [%s]}`, queryRaw, arguments)

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
	if t.Target == 0 {
		return fmt.Errorf("target key cannot be empty in exchange class transaction")
	}

	groupId := uuid.New()

	queryRaw := `INSERT INTO bank_transactions (transaction_type, transaction_amount, user_id, group_uuid) VALUES ($1, $2, $3, $4)`
	argumentsFrom := fmt.Sprintf(`[%q, %d, %d, %q]`, t.Type, -t.Amount, t.Origin, groupId)
	argumentsTo := fmt.Sprintf(`[%q, %d, %d, %q]`, t.Type, t.Amount, t.Target, groupId)
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
