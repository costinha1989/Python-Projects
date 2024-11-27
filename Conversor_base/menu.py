from conversor import converter_para_decimal, converter_de_decimal


def menu():
    """Exibe o menu para o utilizador."""
    while True:
        try:
            borigem = int(input("Número de base original (2, 8, 10, 16): "))
            if borigem not in [2, 8, 10, 16]:
                print("Base de origem inválida! Tente novamente.")
                continue

            num = input(f"Insira o número na base {borigem}: ")
            num_decimal = converter_para_decimal(num, borigem)

            if num_decimal is None:
                print("Número ou base de origem inválida! Tente novamente.")
                continue

            bdestino = int(input("Insere a base de destino (2, 8, 10, 16): "))
            if bdestino not in [2, 8, 10, 16]:
                print("Base de destino inválida! Tente novamente.")
                continue

            result = converter_de_decimal(num_decimal, bdestino)
            print(f"Valor: {result}")

            # Perguntar se o utilizador quer fazer outra conversão
            cont = input("Nova conversão? (s/n): ").strip().lower()
            if cont != 's':
                print("Obrigado por ter utilizado a calculadora!")
                break

        except ValueError:
            print("Entrada inválida! Tente novamente.")
