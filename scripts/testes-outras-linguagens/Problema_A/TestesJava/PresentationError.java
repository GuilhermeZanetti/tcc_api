import java.util.Scanner;
import java.text.DecimalFormat;
import java.util.Locale;

public class PresentationError {
    public static void main(String[] args) {
        // Configura o Scanner para usar ponto como separador decimal
        Scanner scanner = new Scanner(System.in).useLocale(Locale.US);
        
        double P = scanner.nextDouble();
        double AP = scanner.nextDouble();
        double TB = scanner.nextDouble();
        
        // Cálculo correto
        double A1 = (P * 7.0 + AP * 2.0 + TB * 1.0) / 10.0;
        
        // --- ERRO DE APRESENTAÇÃO INTENCIONAL (ESPAÇOS EXTRAS E NOVA LINHA) ---
        // Adiciona espaços desnecessários ("    " e "  ") e usa println.
        
        // DecimalFormat para garantir a formatação de 3 casas
        DecimalFormat df = new DecimalFormat("0.000", new java.text.DecimalFormatSymbols(Locale.US));
        
        String output = "    " + df.format(A1) + "  ";
        
        // Console.println adiciona uma quebra de linha, o que causará PE
        System.out.println(output); 
        
        scanner.close();
    }
}