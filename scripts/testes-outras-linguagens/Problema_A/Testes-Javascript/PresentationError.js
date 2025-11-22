const fs = require('fs');
const input = fs.readFileSync('/dev/stdin', 'utf-8').trim().split(/\s+/);

if (input.length >= 3) {
    const P = parseFloat(input[0]);
    const AP = parseFloat(input[1]);
    const TB = parseFloat(input[2]);

    const media = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;

    // Imprime APENAS o número, sem o \n final
    process.stdout.write(media.toFixed(3));
}