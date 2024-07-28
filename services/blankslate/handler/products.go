package handler

import (
	"Alexjhz07/GoBot/services/blankslate/data"
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
	p.l.Println("Handle GET")
	if r.Method == "GET" {
		p.getProducts(rw, r)
	} else if r.Method == "POST" {
		p.addProducts(rw, r)
	} else {
		http.Error(rw, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func (p *Products) getProducts(rw http.ResponseWriter, r *http.Request) {
	lp := data.GetProducts()

	err := lp.ToJSON(rw)
	if err != nil {
		http.Error(rw, "Could not marshal json: ", http.StatusBadRequest)
	}
}

func (p *Products) addProducts(rw http.ResponseWriter, r *http.Request) {
	p.l.Println("Handle POST")

	prod := &data.Product{}
	err := prod.FromJSON(r.Body)
	if err != nil {
		http.Error(rw, "Could not unmarshal json: ", http.StatusBadRequest)
		return
	}
	data.AddProduct(prod)

	p.l.Printf("Prod: %#v", prod)
}
