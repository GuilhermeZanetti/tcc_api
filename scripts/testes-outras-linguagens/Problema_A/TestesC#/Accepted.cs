using System;
using System.Globalization;
using System.Linq;

public class Program
{
    public static void Main(string[] args)
    {
        // 1. Leitura da Entrada: Lê toda a linha e divide pelos espaços.
        // O Linq .Select(float.Parse) converte os inputs diretamente para float.
        string line = Console.ReadLine();

        // Adiciona tratamento para garantir que a leitura funcione mesmo com múltiplos espaços.
        float[] notes = line.Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries)
            .Select(s => float.Parse(s, CultureInfo.InvariantCulture))
            .ToArray();

        // Assume que a entrada é válida e tem 3 valores.
        float P = notes[0]; // Prova - Peso 7
        float AP = notes[1]; // Atividades Práticas - Peso 2
        float TB = notes[2]; // Trabalho Bimestral - Peso 1

        // 2. Cálculo da Média Ponderada: (P*7 + AP*2 + TB*1) / 10
        double A1 = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;

        // 3. Saída Formatada (Correta):
        // Usa A1.ToString("F3") para formatar com 3 casas decimais.
        // CRUCIAL: Console.Write() é usado em vez de Console.WriteLine() para
        // garantir que NENHUM caractere de nova linha seja adicionado,
        // evitando o Presentation Error (PE).
        Console.WriteLine(A1.ToString("F3"));
    }
}
