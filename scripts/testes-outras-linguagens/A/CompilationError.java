import java.util.Scanner;

// --- ERRO DE COMPILAÇÃO INTENCIONAL (SINTAXE INVÁLIDA) ---
// O caractere '@' solto fora de um contexto de anotação causa falha na compilação.
@

public class CompilationError {
    public static void main(String[] args) {
        // O código de leitura e cálculo está correto, mas nunca será compilado.
        Scanner scanner = new Scanner(System.in);
        
        double P = scanner.nextDouble();
        double AP = scanner.nextDouble();
        double TB = scanner.nextDouble();
        
        double A1 = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;
        
        // Uso de printf para formatar e evitar quebra de linha
        System.out.printf("%.3f", A1);
        scanner.close();
    }
}