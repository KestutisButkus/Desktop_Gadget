import json

import requests
# import json
# from PIL import Image
# from io import BytesIO
from config import key, location

hpa_to_mmhg = 0.75006

def get_weather():
    api_key = key
    city = location
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=4))
        # weather = data['weather'][0]['description']
        city_name = data['name']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        wind_deg = data['wind']['deg']
        pressure_hpa = data['main']['pressure']
        pressure_mmhg = hpa_to_mmhg * pressure_hpa
        icon = data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon}.png"

        # Generuojame vėjo krypties ikonos URL (naudosime rodykles, nurodančias kryptį)
        if 350 <= wind_deg < 10:
            wind_direction = 'N'
        elif 10 <= wind_deg < 80:
            wind_direction = 'NE'
        elif 80 <= wind_deg < 100:
            wind_direction = 'E'
        elif 100 <= wind_deg < 170:
            wind_direction = 'SE'
        elif 170 <= wind_deg < 190:
            wind_direction = 'S'
        elif 190 <= wind_deg < 260:
            wind_direction = 'SW'
        elif 260 <= wind_deg < 280:
            wind_direction = 'W'
        else:
            wind_direction = 'NW'

        weather_info = (
            f"Orų prognozė mieste {city_name}\n"
            # f"Oras: {weather}\n"
            f"Temperatūra: {temp}°C\n"
            f"Jaučiasi kaip: {feels_like}°C\n"
            f"Drėgnumas: {humidity}%\n"
            f"Vėjo greitis: {wind_speed} m/s\n"
            f"Vėjo kryptis: {wind_deg}° {wind_direction}\n"
            f"Slėgis: {pressure_hpa} pHa, {pressure_mmhg:.1f} mmHg"
            )
        print(weather_info)

        return weather_info, icon_url
    else:
        return f"Orų prognozės gauti nepavyko (kodo {response.status_code} klaida).", None


get_weather()