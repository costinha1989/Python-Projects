# menu.py
import os
import time
import geolocation
import file_operations
import pdf_export
import map_operations

def main_menu():
    txt_file = "locations.txt"
    print("Bem-vindo ao sistema de localizações!")
    while True:
        print("\nMENU:")
        print("1 - Introduzir Registo")
        print("2 - Visualizar conteúdo do arquivo")
        print("3 - Visualizar Mapa")
        print("4 - Exportar para PDF")
        print("5 - Sair")

        choice = input("Escolha uma opção: ")

        if choice == "1":
            locations = []

            while True:
                jid = input("Digite o JID (ou '0' para fechar): ")
                if jid.lower() == '0':
                    print("A voltar ao menu inicial...")
                    break

                localidade = input("Digite a Localidade: ")
                city = input("Digite o nome da cidade: ")
                country = input("Digite o nome do país: ")
                grupo = input("Digite o Grupo: ")
                divisao = input("Digite a Divisão: ")

                location = geolocation.geocode_location(city, country, localidade)
                locations.append({
                    "JID": jid,
                    "Localidade": localidade,
                    "Cidade": city,
                    "País": country,
                    "Grupo": grupo,
                    "Divisão": divisao,
                    "Location": location
                })
                print("Localização adicionada com sucesso.\n")

            if locations:
                file_operations.save_locations_to_file(locations, txt_file)
                print("Localizações salvas em 'locations.txt'.")
        elif choice == "2":
            if os.path.exists(txt_file):
                locations = file_operations.read_locations_from_file(txt_file)
                if locations:
                    for loc in locations:
                        print(f"JID: {loc['JID']}, Localidade: {loc['Localidade']}, Cidade: {loc['Cidade']}, País: {loc['País']}, Grupo: {loc['Grupo']}, Divisão: {loc['Divisão']}")
                else:
                    print("O arquivo está vazio.")
            else:
                print(f"O arquivo '{txt_file}' não existe.")
        elif choice == "3":
            if os.path.exists(txt_file):
                locations = file_operations.read_locations_from_file(txt_file)
                if locations:
                    map_operations.generate_map(locations)
                else:
                    print("Nenhuma localização encontrada.")
            else:
                print("Nenhuma localização encontrada. Registre locais antes de visualizar o mapa.")
        elif choice == "4":
            if os.path.exists(txt_file):
                locations = file_operations.read_locations_from_file(txt_file)
                if locations:
                    pdf_export.export_to_pdf(locations, txt_file)
                else:
                    print("Não existe dados para exportação.")
            else:
                print(f"O arquivo '{txt_file}' não existe.")
        elif choice == "5":
            print("Encerrando o programa.")
            time.sleep(1)  # Faz com que o programa encerre após 1 segundo
            break
        else:
            print("Opção inválida. Escolha novamente.")

if __name__ == "__main__":
    main_menu()
