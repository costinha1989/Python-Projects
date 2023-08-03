# geolocation.py
from geopy.geocoders import Nominatim

def geocode_location(city, country, locality=None):
    address = f"{locality + ', ' if locality else ''}{city}, {country}"
    geolocator = Nominatim(user_agent="map_app")
    location = geolocator.geocode(address)

    if location is None:
        print(f"Não foi possível encontrar a localização para o endereço: {address}")
        return None

    return (location.latitude, location.longitude)
