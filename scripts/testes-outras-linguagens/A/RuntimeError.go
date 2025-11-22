package main

import (
	"fmt"
)

func main() {
	var p, ap, tb float64
	
	// Lê os dados para simular um fluxo normal inicial
	fmt.Scan(&p, &ap, &tb)

	// --- ERRO DE TEMPO DE EXECUÇÃO INTENCIONAL ---
	// Declaramos um ponteiro para inteiro, mas não o inicializamos (ele é nil).
	var ponteiroInvalido *int

	// Tentar ler o valor de um ponteiro nil causa um "panic" no Go.
	// Isso gera um erro no stderr que seu juiz classificará como RUNTIME ERROR.
	fmt.Println(*ponteiroInvalido)
}