# file_operations.py
from pathlib import Path

def save_locations_to_file(locations, filename):
    with open(filename, "a") as file:
        for loc in locations:
            if loc['Location'] is not None:
                file.write(f"{loc['JID']},{loc['Localidade']},{loc['Cidade']},{loc['País']},{loc['Grupo']},{loc['Divisão']},{loc['Location'][0]},{loc['Location'][1]}\n")
            else:
                print(f"Aviso: Localização ausente para o JID '{loc['JID']}'. Essa entrada não será salva.")

def read_locations_from_file(filename):
    locations = []
    with open(filename, "r") as file:
        for line in file:
            jid, localidade, city, country, grupo, divisao, lat, lon = line.strip().split(',')
            locations.append({
                "JID": jid,
                "Localidade": localidade,
                "Cidade": city,
                "País": country,
                "Grupo": grupo,
                "Divisão": divisao,
                "Location": (float(lat), float(lon))
            })
    return locations
