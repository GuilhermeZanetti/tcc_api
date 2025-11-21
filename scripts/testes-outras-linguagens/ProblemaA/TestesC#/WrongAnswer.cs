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
        
        // --- CÁLCULO INCORRETO INTENCIONAL ---
        // Usando peso 1 para todas as notas e dividindo por 3 (média simples),
        // em vez da média ponderada correta.
        double somaIncorreta = P + AP + TB;
        double A1 = somaIncorreta / 3.0; // O valor final estará errado (WA)
        
        // A saída está formatada corretamente, mas o VALOR está errado.
        Console.Write(A1.ToString("F3"));
    }
}