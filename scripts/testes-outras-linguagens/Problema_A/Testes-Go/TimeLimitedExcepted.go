package main

import (
	"fmt"
)

func main() {
	var p, ap, tb float64
    
	fmt.Scan(&p, &ap, &tb)

	a1 := (p*7.0 + ap*2.0 + tb*1.0) / 10.0
    
    // LOOP INFINITO INTENCIONAL
    // O programa trava aqui, excedendo o limite de tempo do juiz.
    for {
        // O corpo do loop é vazio, garantindo a execução contínua e desperdiçando tempo.
    }
    
	// Esta linha nunca será alcançada:
	fmt.Printf("%.3f", a1)
}