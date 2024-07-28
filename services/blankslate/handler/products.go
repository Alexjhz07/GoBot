package handler

import (
	"Alexjhz07/GoBot/services/blankslate/data"
	"fmt"
	"log"
	"net/http"
	"regexp"
	"strconv"
)

type Products struct {
	l *log.Logger
}

func NewProducts(l *log.Logger) *Products {
	return &Products{l}
}

func (p *Products) ServeHTTP(rw http.ResponseWriter, r *http.Request) {
	if r.Method == "GET" {
		p.getProducts(rw, r)
	} else if r.Method == "POST" {
		p.addProducts(rw, r)
	} else if r.Method == "PUT" {
		p.editProduct(rw, r)
	} else {
		http.Error(rw, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func (p *Products) getProducts(rw http.ResponseWriter, r *http.Request) {
	p.l.Println("Handle GET")

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
}

func (p *Products) editProduct(rw http.ResponseWriter, r *http.Request) {
	p.l.Println("Handle PUT")

	reg := regexp.MustCompile(`/([0-9]+)`)
	g := reg.FindAllStringSubmatch(r.URL.Path, -1)

	if len(g) != 1 || len(g[0]) != 2 {
		http.Error(rw, "Length of id must be 1", http.StatusBadRequest)
		return
	}

	idString := g[0][1]
	id, err := strconv.Atoi(idString)
	if err != nil {
		http.Error(rw, "Unable to parse ID", http.StatusBadRequest)
		return
	}

	prod := &data.Product{}
	err = prod.FromJSON(r.Body)
	if err != nil {
		http.Error(rw, "Could not unmarshal json", http.StatusBadRequest)
		return
	}

	err = data.UpdateProduct(id, prod)
	if err != nil {
		http.Error(rw, fmt.Sprintf("Could not update: %s", err), http.StatusBadRequest)
		return
	}
}
