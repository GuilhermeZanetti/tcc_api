<?php

// Lê a linha de entrada
$input_line = trim(fgets(STDIN));
$notes = explode(' ', $input_line);

$P = (float)$notes[0];
$AP = (float)$notes[1];
$TB = (float)$notes[2];

// Cálculo correto
$A1 = ($P * 7.0 + $AP * 2.0 + $TB * 1.0) / 10.0;

// --- ERRO DE APRESENTAÇÃO INTENCIONAL (ESPAÇOS EXTRAS) ---
// O juiz espera APENAS o número. A adição de espaços em branco antes
// e depois do número formatado irá causar o Presentation Error (PE).
// Removemos o '\n' e adicionamos espaços ('    ' e '  ') para isolar a causa.
echo "    " . number_format($A1, 3, '.', '') . "  ";
?>