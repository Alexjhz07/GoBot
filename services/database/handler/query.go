package handler

import (
	"fmt"
	"net/http"
)

type Query struct{}

func (q *Query) AnyQuery(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Here")
}
