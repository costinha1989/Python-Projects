import data_manager
import os
from file_handler import delete_json


def main_menu():
    while True:
        clear_console()

        print("\nMenu Principal")
        print("\n")
        print("1. Importar dados de ficheiro CSV")
        print("2. Exportar mapa OpenstreetMaps")
        print("3. Eliminar dados antigos")
        print("4. Sair")

        choice = input("Escolha uma opção: ")

        if choice == '1':
            csv_file_path = input("Introduza o caminho do ficheiro CSV: ")
            data_manager.import_from_csv(csv_file_path)
        elif choice == '2':
            data_manager.show_on_map()
        elif choice == '3':
            confirm = input("Tem certeza que deseja eliminar os dados antigos? (s/n): ")
            if confirm.lower() == 's':
                delete_json()
            else:
                print("Operação anulada.")
        elif choice == '4':
            print("\nObrigado por utilizar o software!")
            break
        else:
            print("Opção inválida, por favor tente novamente.")


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    main_menu()
