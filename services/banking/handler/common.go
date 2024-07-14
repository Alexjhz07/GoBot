package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
)

var transactionTypesAll = map[string]bool{
	"initial":  true,
	"daily":    true,
	"weekly":   true,
	"monthly":  true,
	"transfer": true,
	"flip":     true,
	"wordle":   true,
}

var transactionTypesSingle = map[string]bool{
	"initial": true,
	"daily":   true,
	"weekly":  true,
	"monthly": true,
	"flip":    true,
	"wordle":  true,
}

var transactionTypesExchange = map[string]bool{
	"transfer": true,
}

func parseTransactionRequestJSON(r *http.Request) (*TransactionRequest, error) {
	decoder := json.NewDecoder(r.Body)

	ret := &TransactionRequest{}
	err := decoder.Decode(ret)
	if err != nil {
		return nil, err
	}

	if !transactionTypesAll[ret.Type] {
		return nil, fmt.Errorf("error %q is not a valid type", ret.Type)
	}

	return ret, nil
}

func parseAccountRequestJSON(r *http.Request) (*AccountRequest, error) {
	decoder := json.NewDecoder(r.Body)

	ret := &AccountRequest{}
	err := decoder.Decode(ret)
	if err != nil {
		return nil, err
	}

	if len(ret.Accounts) == 0 {
		return nil, fmt.Errorf("error account query length cannot be 0")
	}

	return ret, nil
}
