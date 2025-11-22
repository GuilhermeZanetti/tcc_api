<?php

// Lê a linha de entrada
$input_line = trim(fgets(STDIN));
$notes = explode(' ', $input_line);

$P = (float)$notes[0];
$AP = (float)$notes[1];
$TB = (float)$notes[2];

// --- LOOP INFINITO INTENCIONAL ---
// O programa ficará preso aqui, excedendo o tempo limite (TLE).
while (true) {
    // Incrementa uma variável para que o loop não seja otimizado, 
    // mas o programa nunca sairá daqui.
    $i++; 
}

// O código correto abaixo nunca será alcançado
$A1 = ($P * 7.0 + $AP * 2.0 + $TB * 1.0) / 10.0;
echo number_format($A1, 3, '.', '') . "\n";
?>