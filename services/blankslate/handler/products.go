package handler

import (
	"Alexjhz07/GoBot/services/blankslate/data"
	"encoding/json"
	"log"
	"net/http"
)

type Products struct {
	l *log.Logger
}

func NewProducts(l *log.Logger) *Products {
	return &Products{l}
}

func (p *Products) ServeHTTP(rw http.ResponseWriter, r *http.Request) {
	lp := data.GetProducts()

	bytes, err := json.Marshal(lp)
	if err != nil {
		http.Error(rw, "Could not marshal json: ", http.StatusBadRequest)
	}

	rw.Write(bytes)
}
