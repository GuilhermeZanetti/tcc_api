package main

import (
"fmt"
)

func main() {
var p, ap, tb float64
    
fmt.Scan(&p, &ap, &tb)
    
    // --- ERRO DE COMPILAÇÃO INTENCIONAL ---
    // Tentativa de chamar uma função inexistente no pacote "fmt".
    // Isso deve resultar em um erro do tipo "fmt.FuncaoInexistente undefined".
    fmt.FuncaoInexistente("Isso não deve compilar") 

    // O código de cálculo correto está abaixo, mas não será compilado.
    a1 := (p*7.0 + ap*2.0 + tb*1.0) / 10.0

fmt.Printf("%.3f", a1)
}
