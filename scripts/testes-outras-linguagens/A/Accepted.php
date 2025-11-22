<?php

// Define a função para leitura do input (útil em alguns ambientes de submissão)
$input_line = trim(fgets(STDIN));

// Divide a linha de entrada em um array de strings usando o espaço como delimitador.
$notes = explode(' ', $input_line);

// Converte os valores de string para float e atribui às variáveis
// Assume-se que a entrada terá P, AP e TB, em ordem.
$P = isset($notes[0]) ? (float)$notes[0] : 0.0;   // Prova - Peso 7
$AP = isset($notes[1]) ? (float)$notes[1] : 0.0;  // Atividades Práticas - Peso 2
$TB = isset($notes[2]) ? (float)$notes[2] : 0.0;  // Trabalho Bimestral - Peso 1

// Fórmula da Média Ponderada: (P*7 + AP*2 + TB*1) / 10
$A1 = ($P * 7.0 + $AP * 2.0 + $TB * 1.0) / 10.0;

// A saída deve ter um único número real, com 3 casas decimais.
// number_format formata o número com 3 decimais, usando '.' como separador.

$result = number_format($A1, 3, '.', ''); 

echo $result."\n"

?>