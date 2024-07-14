package handler

import (
	"fmt"
	"net/http"
	"strings"
)

type AccountRequest struct {
	Accounts []int64 `json:"accounts"`
}

type Account struct{}

func (a *Account) PostAccount(w http.ResponseWriter, r *http.Request) {
	parsedRequest, err := parseAccountRequestJSON(r)
	if err != nil {
		fmt.Println("error decoding incoming request: ", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	var placeholderBuilder strings.Builder
	requestEndIndex := len(parsedRequest.Accounts) - 1

	placeholderBuilder.WriteString("(")
	for i := range parsedRequest.Accounts {
		placeholderBuilder.WriteString(fmt.Sprintf("$%d", i+1))
		if i < requestEndIndex {
			placeholderBuilder.WriteString(",")
		}
	}
	placeholderBuilder.WriteString(")")

	queryRaw := fmt.Sprintf("SELECT user_id, SUM(transaction_amount) FROM bank_transactions GROUP BY user_id WHERE user_id IN %s", placeholderBuilder.String())

	fmt.Println(queryRaw)

	// arguments := fmt.Sprintf(`[%q, %d, %d, %q]`, t.Type, t.Amount, t.Origin, groupId)
	// queryString := fmt.Sprintf(`{"queries": [%q], "arguments": [%s]}`, queryRaw, arguments)

	// requestBody := bytes.NewReader([]byte(queryString))

	// response, err := http.Post("http://localhost:3815/api/v1/exec", "application/json", requestBody)
	// if err != nil {
	// 	return err
	// }

	// if response.StatusCode != http.StatusOK {
	// 	return fmt.Errorf("status code not 200: %d", response.StatusCode)
	// }

	w.WriteHeader(http.StatusOK)
}
