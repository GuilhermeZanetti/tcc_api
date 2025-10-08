import java.util.Scanner;

public class ProblemaG {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int N = sc.nextInt(); // número de participantes
        int H = sc.nextInt(); // pizzas de 12 pedaços
        int G = sc.nextInt(); // pizzas de 8 pedaços
        int M = sc.nextInt(); // pizzas de 6 pedaços

        int total = H * 12 + G * 8 + M * 6;
        int consumidos = Math.min(N, total);
        int sobra = total - consumidos;

        System.out.println(sobra);

        sc.close();
    }
}