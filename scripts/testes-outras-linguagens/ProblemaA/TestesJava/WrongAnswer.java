import java.util.Scanner;
import java.text.DecimalFormat;
import java.util.Locale;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in).useLocale(Locale.US);
        
        double P = scanner.nextDouble();
        double AP = scanner.nextDouble();
        double TB = scanner.nextDouble();
        
        // --- CÁLCULO INCORRETO INTENCIONAL ---
        // Usando peso 1 para todas as notas e dividindo por 3 (média simples),
        // em vez da média ponderada correta.
        double somaIncorreta = P + AP + TB;
        double A1 = somaIncorreta / 3.0; // O valor final estará errado (WA)
        
        // A saída está formatada corretamente, mas o VALOR está errado.
        System.out.printf(Locale.US, "%.3f", A1);
        scanner.close();
    }
}