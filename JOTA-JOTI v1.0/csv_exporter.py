import csv
from file_handler import load_records


def export_to_csv():
    records = load_records()

    if not records:
        print("Não existe registos para exportar.")
        return

    csv_file_name = "registos.csv"

    with open(csv_file_name, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        header = ["JID", "Localidade", "País", "Grupo", "Divisão", "Timestamp"]  # Escreve o cabeçalho
        writer.writerow(header)

        for record in records:  # Escreve os registos
            row = [
                record.get("JID"),
                record.get("Localidade"),
                record.get("País"),
                record.get("Grupo"),
                record.get("Divisão"),
                record.get("Timestamp")
            ]
            writer.writerow(row)

    print(f"Ficheiro exportado com sucesso.")
