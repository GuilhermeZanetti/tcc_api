<?php

// Lê a linha de entrada
$input_line = trim(fgets(STDIN));
$notes = explode(' ', $input_line);

$P = (float)$notes[0];
$AP = (float)$notes[1];
$TB = (float)$notes[2];

// --- CÁLCULO INCORRETO INTENCIONAL ---
// Usando peso 1 para todas as notas e dividindo por 3 (média simples),
// em vez da média ponderada (pesos 7, 2, 1 e divisor 10).
$somaIncorreta = $P + $AP + $TB;
$A1 = $somaIncorreta / 3.0; // O resultado final será diferente do esperado (WA)

// A saída está formatada corretamente, mas o VALOR está errado.
echo number_format($A1, 3, '.', '') . "\n";
?>