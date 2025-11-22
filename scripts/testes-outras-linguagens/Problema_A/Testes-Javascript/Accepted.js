const fs = require('fs');
// Lê toda a entrada do stdin
const input = fs.readFileSync('/dev/stdin', 'utf-8').trim().split(/\s+/);

if (input.length >= 3) {
    const P = parseFloat(input[0]);
    const AP = parseFloat(input[1]);
    const TB = parseFloat(input[2]);

    // Pesos: Prova(7), Atividades(2), Trabalho(1)
    const media = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;

    // Imprime com 3 casas decimais e quebra de linha (padrão do console.log)
    console.log(media.toFixed(3));
}