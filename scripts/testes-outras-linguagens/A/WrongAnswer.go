package main

import (
	"fmt"
)

func main() {
	var p, ap, tb float64
    
	fmt.Scan(&p, &ap, &tb)

	// --- CÁLCULO INCORRETO INTENCIONAL ---
	// Usando peso 1 para todas as notas e dividindo por 3 (média simples),
    // em vez da média ponderada (pesos 7, 2, 1 e divisor 10).
    
	somaIncorreta := p + ap + tb
    a1 := somaIncorreta / 3.0 // O resultado final será diferente do esperado (WA)

	// A saída está formatada corretamente, mas o VALOR está errado.
	fmt.Printf("%.3f", a1)
}