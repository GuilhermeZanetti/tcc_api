using System;

public class Program
{
    public static void Main(string[] args)
    {
        int N = int.Parse(Console.ReadLine()); 
        int H = int.Parse(Console.ReadLine()); 
        int G = int.Parse(Console.ReadLine());
        int M = int.Parse(Console.ReadLine()); 
                
        int totalPedacos = (H * 12) + (G * 8) + (M * 6);
        
        int pedacosDistribuidos = Math.Min(N, totalPedacos);

        int pedacosQueSobram = totalPedacos - pedacosDistribuidos;
        
        Console.WriteLine(pedacosQueSobram);
    }
}

/*

namespace csharpProject;

class Program
{
    static void Main(string[] args)
    {
         int N = int.Parse(Console.ReadLine()); 
        int H = int.Parse(Console.ReadLine()); 
        int G = int.Parse(Console.ReadLine());
        int M = int.Parse(Console.ReadLine()); 
                
        int totalPedacos = (H * 12) + (G * 8) + (M * 6);
        
        int pedacosDistribuidos = Math.Min(N, totalPedacos);

        int pedacosQueSobram = totalPedacos - pedacosDistribuidos;
        
        Console.WriteLine(pedacosQueSobram);
    }
}

*/