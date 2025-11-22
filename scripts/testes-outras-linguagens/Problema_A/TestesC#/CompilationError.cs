using System;

public class Program
{
    // --- ERRO DE COMPILAÇÃO INTENCIONAL (SINTAXE INVÁLIDA) ---
    // O caractere '@' solto fora de uma string ou contexto especial causará falha na compilação.
    @

    public static void Main(string[] args)
    {
        // O código de leitura e cálculo está correto, mas nunca será compilado.
        string[] input = Console.ReadLine().Split(' ');
        
        float P = float.Parse(input[0]);
        float AP = float.Parse(input[1]);
        float TB = float.Parse(input[2]);
        
        double A1 = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;
        
        Console.Write(A1.ToString("F3"));
    }
}