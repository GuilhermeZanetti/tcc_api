import java.util.Scanner;

public class TimeLimitedExcepted {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        double P = scanner.nextDouble();
        double AP = scanner.nextDouble();
        double TB = scanner.nextDouble();
        
        // Cálculo correto
        double A1 = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;
        
        // --- LOOP INFINITO INTENCIONAL ---
        // O programa fica preso neste loop, excedendo o tempo limite (TLE).
        while (true) {
            // O corpo do loop é vazio, garantindo a execução contínua e desperdiçando tempo.
        }
        
        // A saída nunca será alcançada.
        // System.out.printf("%.3f", A1);
        // scanner.close();
    }
}