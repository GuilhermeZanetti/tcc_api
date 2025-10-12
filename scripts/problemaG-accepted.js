
function main() {
    const N = parseInt(readline(), 10);
    const H = parseInt(readline(), 10);
    const G = parseInt(readline(), 10);
    const M = parseInt(readline(), 10);

    const totalPedaços = (H * 12) + (G * 8) + (M * 6);
    const pedaçosDistribuidos = Math.min(N, totalPedaços);
    const pedaçosQueSobram = totalPedaços - pedaçosDistribuidos;

    console.log(pedaçosQueSobram);
}
