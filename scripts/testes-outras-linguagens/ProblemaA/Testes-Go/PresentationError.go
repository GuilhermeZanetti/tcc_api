package main

import (
	"fmt"
	"os"
)

func main() {
	// Variáveis para armazenar as notas
	var p, ap, tb float64

	// Leitura das três notas (Prova, Atividades Práticas, Trabalho)
	// Espera-se que a entrada forneça as três notas separadas por espaço
	_, err := fmt.Scanf("%f %f %f", &p, &ap, &tb)

	// Verifica se houve erro na leitura e se o erro não é EOF (End of File)
	if err != nil && err.Error() != "EOF" {
		// Em um ambiente de competição, muitas vezes não se imprime erros
		// Mas aqui incluímos para fins de depuração
		// fmt.Fprintln(os.Stderr, "Erro ao ler a entrada:", err)
		os.Exit(1)
	}

	// Fórmula da Média Ponderada: (P*7 + AP*2 + TB*1) / (7+2+1)
	a1 := (p*7.0 + ap*2.0 + tb*1.0) / 10.0

	// A saída deve ter um único número real, com 3 casas decimais.
	// O formatador "%.3f" garante 3 casas decimais.
	fmt.Printf("%.3f\n", a1)
}