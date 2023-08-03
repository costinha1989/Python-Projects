# map_operations.py
import folium

def generate_map(locations):
    map_osm = folium.Map(location=locations[0]["Location"], zoom_start=12)

    for loc in locations:
        popup_content = f"JID: {loc['JID']}<br>" \
                        f"Localidade: {loc['Localidade']}<br>" \
                        f"Cidade: {loc['Cidade']}<br>" \
                        f"País: {loc['País']}<br>" \
                        f"Grupo: {loc['Grupo']}<br>" \
                        f"Divisão: {loc['Divisão']}<br>"

        folium.Marker(location=loc["Location"], popup=popup_content).add_to(map_osm)

    map_osm.save("map.html")
    print("Mapa gerado com sucesso. Abra o ficheiro 'map.html' no seu browser.")
