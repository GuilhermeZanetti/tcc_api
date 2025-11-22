const fs = require('fs');

function main() {
    let objetoInexistente;
    
    // Tenta acessar uma propriedade de uma variável undefined
    // Isso lança: TypeError: Cannot read properties of undefined
    console.log(objetoInexistente.valor);
}

main();