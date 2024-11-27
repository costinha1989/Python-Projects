import folium
from geopy.geocoders import Nominatim
from file_handler import load_records

def get_coordinates(localidade, pais):
    geolocator = Nominatim(user_agent="jota_joti_locator")
    try:
        location = geolocator.geocode(f"{localidade}, {pais}")
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Erro ao obter coordenadas para {localidade}, {pais}: {e}")
    return None, None

def show_on_map(save_path="map.html"):
    records = load_records()

    # Centralizar o mapa numa posição arbitrária
    map_center = [20.0, 0.0]
    map_obj = folium.Map(location=map_center, zoom_start=2)

    for record in records:
        localidade = record.get('Localidade', 'Desconhecida')
        pais = record.get('País', 'Desconhecido')
        jid = record.get('JID', 'N/A')
        timestamp = record.get('Timestamp', 'N/A')
        grupo = record.get('Grupo', 'N/A')
        divisao = record.get('Divisão', 'N/A')

        latitude, longitude = get_coordinates(localidade, pais)

        if latitude is not None and longitude is not None:
            popup_content = (
                f"{localidade}, {pais}<br>"
                f"JID: {jid}<br>"
                f"Grupo: {grupo}<br>"
                f"Divisão: {divisao}<br>"
                f"Timestamp: {timestamp}"
            )
            folium.Marker(
                location=[latitude, longitude],
                popup=popup_content,
                tooltip=f"JID: {jid}"
            ).add_to(map_obj)
        else:
            print(f"Não foi possível encontrar {localidade} e {pais}")

    # Guarda o mapa no caminho fornecido
    map_obj.save(save_path)
    print(f"Mapa guardado com sucesso em {save_path}.")
