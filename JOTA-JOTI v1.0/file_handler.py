import json
import os

JSON_FILE_PATH = 'data.json'


def load_records():
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_records(records):
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(records, file, indent=4, ensure_ascii=False)


def delete_json():
    if os.path.exists(JSON_FILE_PATH):
        os.remove(JSON_FILE_PATH)
        print('Dados eliminados com sucesso.')
    else:
        print("Não existem dados para eliminar.")
