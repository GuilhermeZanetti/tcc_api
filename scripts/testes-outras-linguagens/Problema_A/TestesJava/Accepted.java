import java.util.Scanner;
import java.util.Locale;

public class Main {
    public static void main(String[] args) {
        // 1. Configuração e Leitura: 
        // Usa Locale.US para garantir que o Scanner interprete o input (e.g., "4.358") 
        // corretamente, independentemente das configurações regionais do juiz.
        Scanner scanner = new Scanner(System.in).useLocale(Locale.US);
        
        double P = scanner.nextDouble();   // Prova - Peso 7
        double AP = scanner.nextDouble();  // Atividades Práticas - Peso 2
        double TB = scanner.nextDouble();  // Trabalho Bimestral - Peso 1

        // 2. Cálculo da Média Ponderada: (P*7 + AP*2 + TB*1) / 10
        double A1 = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;

        // 3. Saída Formatada (Correta):
        // Usa System.out.printf com Locale.US para garantir que o separador decimal seja o ponto.
        // O formato "%.3f" garante 3 casas decimais.
        // CRUCIAL: O printf (sem '\n') evita o Presentation Error (PE).
        System.out.printf(Locale.US, "%.3f", A1);
        
        scanner.close();
    }
}