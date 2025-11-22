<?php

// Lê a linha de entrada
$input_line = trim(fgets(STDIN));
$notes = explode(' ', $input_line);

$P = (float)$notes[0];
$AP = (float)$notes[1];
$TB = (float)$notes[2];

// --- ERRO DE EXECUÇÃO INTENCIONAL (DIVISÃO POR ZERO) ---
$divisor = 0;

// Isso gera um E_WARNING de divisão por zero, que em muitos juízes é um RE.
$P_modificado = $P / $divisor; 

// Acessa uma posição que certamente não existe, gerando um Notice/Warning
// que pode ser tratado como RE pelo juiz.
$erro_acesso = $notes[99]; 

// O cálculo abaixo falhará devido ao P_modificado ser Inf
$A1 = ($P_modificado * 7.0 + $AP * 2.0 + $TB * 1.0) / 10.0;

echo number_format($A1, 3, '.', '') . "\n";
?>