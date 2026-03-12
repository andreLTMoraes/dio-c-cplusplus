#include <stdio.h>

int main() {
    double num1, num2, resultado;
    char operador;

    printf("=================================\n");
    printf("       CALCULADORA SIMPLES       \n");
    printf("=================================\n");
    printf("Operacoes disponiveis: + - * /\n");
    printf("---------------------------------\n");

    printf("Digite o primeiro numero: ");
    scanf("%lf", &num1);

    printf("Digite o operador (+, -, *, /): ");
    scanf(" %c", &operador);

    printf("Digite o segundo numero: ");
    scanf("%lf", &num2);

    printf("---------------------------------\n");

    switch (operador) {
        case '+':
            resultado = num1 + num2;
            printf("Resultado: %.2lf + %.2lf = %.2lf\n", num1, num2, resultado);
            break;

        case '-':
            resultado = num1 - num2;
            printf("Resultado: %.2lf - %.2lf = %.2lf\n", num1, num2, resultado);
            break;

        case '*':
            resultado = num1 * num2;
            printf("Resultado: %.2lf * %.2lf = %.2lf\n", num1, num2, resultado);
            break;

        case '/':
            if (num2 == 0) {
                printf("Erro: divisao por zero nao e permitida!\n");
            } else {
                resultado = num1 / num2;
                printf("Resultado: %.2lf / %.2lf = %.2lf\n", num1, num2, resultado);
            }
            break;

        default:
            printf("Erro: operador invalido '%c'!\n", operador);
            break;
    }

    printf("=================================\n");

    return 0;
}
