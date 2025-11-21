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
        
        // --- ERRO DE EXECUÇÃO INTENCIONAL ---
        // Tentativa de acessar uma posição do array que não existe (IndexOutOfRangeException)
        string erro = input[99]; 
        
        // Tentativa de dividir por zero (apenas se usarmos inteiros, mas ainda assim é um RE)
        int divisor = 0;
        int resultado = 10 / divisor; // Lança DivideByZeroException no runtime
        
        // O cálculo correto abaixo nunca será alcançado
        double A1 = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;
        
        Console.Write(A1.ToString("F3"));
    }
}