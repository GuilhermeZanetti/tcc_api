import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        try {
            // Configura o Scanner para usar ponto como separador decimal
            Scanner scanner = new Scanner(System.in);
            
            double P = scanner.nextDouble();
            double AP = scanner.nextDouble();
            double TB = scanner.nextDouble();
            
            // --- ERRO DE EXECUÇÃO INTENCIONAL ---
            // Tentativa de ler um quarto valor que não existe na entrada,
            // ou tentar dividir por zero, o que causa uma exceção no runtime.
            
            // Causa NoSuchElementException se a entrada tiver apenas 3 números
            double quartoValor = scanner.nextDouble(); 

            // Causa ArithmeticException: / by zero
            int divisor = 0;
            int resultado = 10 / divisor; 
            
            double A1 = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;
            
            System.out.printf("%.3f", A1);
            scanner.close();
            
        } catch (Exception e) {
            // Se o juiz capturar esta exceção, o status será Runtime Error (RE).
            System.err.println("Ocorreu um erro de execução: " + e.getMessage());
        }
    }
}