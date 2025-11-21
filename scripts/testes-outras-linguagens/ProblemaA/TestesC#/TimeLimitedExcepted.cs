using System;
using System.Linq;

public class Program
{
    public static void Main(string[] args)
    {
        string[] input = Console.ReadLine().Split(' ');
        
        float P = float.Parse(input[0]);
        float AP = float.Parse(input[1]);
        float TB = float.Parse(input[2]);
        
        // Cálculo correto
        double A1 = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;
        
        // --- LOOP INFINITO INTENCIONAL ---
        // O programa fica preso neste loop, excedendo o tempo limite (TLE).
        while (true)
        {
            // Operação vazia para garantir que o loop não termine.
        }
        
        // A saída nunca será alcançada.
        Console.Write(A1.ToString("F3"));
    }
}