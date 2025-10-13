<?php
$N = (int)trim(fgets(STDIN));
$H = (int)trim(fgets(STDIN)); 
$G = (int)trim(fgets(STDIN)); 
$M = (int)trim(fgets(STDIN)); 

$totalFatias = ($H * 12) + ($G * 8) + ($M * 6);

$fatiasDistribuidas = min($N, $totalFatias);

$fatiasSobrantes = $totalFatias - $fatiasDistribuidas;

echo $fatiasSobrantes . "\n";

?>