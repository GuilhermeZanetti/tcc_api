package main

import (
	"fmt"
	"os"
)

func main() {
	// Variáveis para armazenar as notas
	var p, ap, tb float64

	// Leitura das três notas (Prova, Atividades Práticas, Trabalho)
	// Usamos o Scanf e tratamos o erro de forma mínima
	_, err := fmt.Scanf("%f %f %f", &p, &ap, &tb)

	if err != nil && err.Error() != "EOF" {
		os.Exit(1)
	}

	// Fórmula da Média Ponderada
	a1 := (p*7.0 + ap*2.0 + tb*1.0) / 10.0
	
	// A saída deve ter um único número real, com 3 casas decimais.
	fmt.Printf("%.3f\n", a1) 
}