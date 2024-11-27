import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from csv_exporter import export_to_csv as csv_export
from file_handler import save_records, load_records, delete_json
from map_viewer import show_on_map as view_map
from utils import get_current_timestamp


def import_sheets(sheet_url):
    # Define o escopo
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Autenticação com as credenciais de serviço
    creds = ServiceAccountCredentials.from_json_keyfile_name('keys/costinha-217509-f9e257140999.json', scope)
    client = gspread.authorize(creds)

    # Abertura da planilha
    sheet = client.open_by_url(sheet_url)
    worksheet = sheet.sheet1  # Seleciona a primeira aba

    # Obtém todos os cabeçalhos da planilha para verificar
    headers = worksheet.row_values(1)
    print("Cabeçalhos na planilha:", headers)  # Imprime os cabeçalhos para verificação

    # Definindo os cabeçalhos esperados - certifique-se de que correspondem exatamente
    expected_headers = ['Canal utilizado', 'Indicativo JOTA (Rádio) ou o JID (Internet)', 'Localidade', 'País', 'Grupo', 'Divisão']

    # Obter todos os dados da planilha
    try:
        data = worksheet.get_all_records(expected_headers=expected_headers)
    except Exception as e:
        print(f"Erro na importação: {e}")
        return

    existing_records = load_records()  # Carrega os registros existentes do JSON

    for row in data:
        record = {
            "Canal utilizado": row.get("Canal utilizado"),
            "JID": row.get("Indicativo JOTA (Rádio) ou o JID (Internet)"),
            "Localidade": row.get("Localidade"),
            "País": row.get("País"),
            "Grupo": row.get("Grupo"),
            "Divisão": row.get("Divisão"),
            "Timestamp": get_current_timestamp()  # ou row.get("Timestamp") se disponível
        }
        existing_records.append(record)

    save_records(existing_records)
    print(f"Dados importados com sucesso do Google Sheets.")


def del_data():
    if load_records():  # Verifica se há registos antes de tentar eliminar
        delete_json()
    else:
        print("Não existem dados para eliminar.")



def add_record():
    jid = input("JID: ")
    localidade = input("Localidade ou cidade: ")
    pais = input("País: ")
    grupo = input("Grupo (Ex: 00): ")
    divisao = input("Divisão (Ex: Alcateia): ")
    canal_utilizado = input("Canal utilizado (Rádio ou Internet): ")

    timestamp = get_current_timestamp()

    record = {
        "Canal utilizado": canal_utilizado,
        "JID": jid,
        "Localidade": localidade,
        "País": pais,
        "Grupo": grupo,
        "Divisão": divisao,
        "Timestamp": timestamp
    }

    existing_records = load_records()  # Carrega os registos existentes
    existing_records.append(record)  # Adiciona o novo registo
    save_records(existing_records)  # Salva a lista atualizada
    print("Registo gravado!")


def del_data():
    delete_json()


def show_last_records():
    records = load_records()
    for record in records[-5:]:
        print(record)


def show_on_map(save_path):
    view_map(save_path)


def export_to_csv():
    csv_export()


def import_from_csv(csv_file_path):
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            existing_records = load_records()  # Carrega os registros existentes do JSON

            for row in csv_reader:
                record = {
                    "Canal utilizado": row.get("Canal utilizado"),
                    "JID": row.get("Indicativo/JID"),
                    "Localidade": row.get("Localidade"),
                    "País": row.get("País"),
                    "Grupo": row.get("Grupo"),
                    "Divisão": row.get("Divisão"),
                    "Timestamp": row.get("Timestamp")
                }
                existing_records.append(record)

            save_records(existing_records)

            print(f"Dados importados com sucesso do ficheiro CSV.")
    except Exception as e:
        print(f"Ocorreu um erro ao importar os dados do ficheiro CSV: {e}")


def save_as_text(file_path):
    try:
        temp_html_path = file_path.replace('.txt', '.html')
        view_map(temp_html_path)

        if not os.path.exists(temp_html_path):
            print(f"Erro: O ficheiro HTML {temp_html_path} não foi encontrado.")
            return

        with open(temp_html_path, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()

        with open(file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(html_content)

        print(f"Dados exportados como TXT com sucesso para o ficheiro {file_path}.")
    except Exception as e:
        print(f"Ocorreu um erro ao exportar o mapa para TXT: {e}")
