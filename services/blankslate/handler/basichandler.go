package handler

import (
	"fmt"
	"io"
	"log"
	"net/http"
)

type BasicHandler struct {
	l *log.Logger
}

func NewBasicHandler(l *log.Logger) *BasicHandler {
	return &BasicHandler{l}
}

func (bh *BasicHandler) ServeHTTP(rw http.ResponseWriter, r *http.Request) {
	bh.l.Println("Log Prints Out")

	d, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(rw, "Error String", http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(rw, "Data: %s", d)
}
