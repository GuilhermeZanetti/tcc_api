<?php

// --- ERRO DE COMPILAÇÃO INTENCIONAL (SINTAXE INVÁLIDA) ---
// O caractere '@' solto fora de uma string ou função não é permitido em PHP.
@

// Erro de sintaxe na palavra-chave (o correto é 'function')
functio main_logic() {
    // Código correto, mas nunca será interpretado
    $input_line = trim(fgets(STDIN));
    $notes = explode(' ', $input_line);
    $P = (float)$notes[0];
    $AP = (float)$notes[1];
    $TB = (float)$notes[2];
    
    $A1 = ($P * 7.0 + $AP * 2.0 + $TB * 1.0) / 10.0;
    
    echo number_format($A1, 3, '.', '') . "\n";
}

main_logic();
?>