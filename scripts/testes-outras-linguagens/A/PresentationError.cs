using System;
using System.Linq;

public class Program
{
    public static void Main(string[] args)
    {
        // Lê a linha de entrada e converte para float
        string[] input = Console.ReadLine().Split(' ');
        
        float P = float.Parse(input[0]);
        float AP = float.Parse(input[1]);
        float TB = float.Parse(input[2]);
        
        // Cálculo correto
        double A1 = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;
        
        // --- ERRO DE APRESENTAÇÃO INTENCIONAL (ESPAÇOS EXTRAS) ---
        // Adiciona espaços desnecessários ("    " e "  ") na saída.
        string output = $"    {A1:F3}  ";
        
        Console.Write(output);
    }
}