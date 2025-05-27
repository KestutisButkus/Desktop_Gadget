# import json
# import os
# import requests
#
# place = "Kaunas"
# url = f"https://api.meteo.lt/v1/places/{place}/forecasts/long-term"
#
# # Atliksime GET užklausą
# response = requests.get(url)
# data = response.json()
# print(json.dumps(data, indent=4))
# # ----------------------------------------------
# # segment = range(0,6)
# # forecast_segment = [data["forecastTimestamps"][i] for i in segment]
# # for forecast in forecast_segment:
# # --------------------------------------------
# forecast = data["forecastTimestamps"][0]
# time_utc = forecast["forecastTimeUtc"]
# print(time_utc, "+2")
# location = data["place"]["name"]  # Vietovė
# temp_now = forecast["airTemperature"]  # Dabartinė temperatūra
# temp_feel = forecast["feelsLikeTemperature"]  # Jaučiama temperatūra
# wind_speed = forecast["windSpeed"]  # Vėjo greitis
# wind_gust = forecast["windGust"]  # Vėjo gūsiai
# wind_degree = forecast["windDirection"]  # Vėjo kryptis (laipsniais)
# cloud_cover = forecast["cloudCover"]  # Debesuotumas
# pressure_hpa = forecast["seaLevelPressure"]  # Slėgis jūros lygyje
# hpa_to_mmhg = 0.75006  # Konversijos koeficientas naudojamas atmosferos slėgio matavimo vienetų konvertavimui.
# pressure_mmhg = pressure_hpa * hpa_to_mmhg  # Slėgis jūros lygyje "Torr"
# relative_humidity = forecast["relativeHumidity"]  # Santykinė drėgmė
# total_precipitation = forecast["totalPrecipitation"]  # Krituliai
# condition_code = forecast["conditionCode"]  # Orų būklė
#
# if 350 <= wind_degree < 10:
#     wind_direction = 'N'
# elif 10 <= wind_degree < 80:
#     wind_direction = 'NE'
# elif 80 <= wind_degree < 100:
#     wind_direction = 'E'
# elif 100 <= wind_degree < 170:
#     wind_direction = 'SE'
# elif 170 <= wind_degree < 190:
#     wind_direction = 'S'
# elif 190 <= wind_degree < 260:
#     wind_direction = 'SW'
# elif 260 <= wind_degree < 280:
#     wind_direction = 'W'
# else:
#     wind_direction = 'NW'
#
# weather_ico = ""
# if condition_code == "cloudy":
#     weather_ico = os.path.abspath("img/cloudy.png")
# elif condition_code == "partly-cloudy":
#     weather_ico = os.path.abspath("img/mostly_clear_day.png")
# elif condition_code == "clear":
#     weather_ico = os.path.abspath("img/clear_day.png")
# elif condition_code == "light-rain":
#     weather_ico = os.path.abspath("img/drizzle.png")
# elif condition_code == "rain":
#     weather_ico = os.path.abspath("img/showers_rain.png")
# elif condition_code == "heavy-rain":
#     weather_ico = os.path.abspath("img/heavy_rain.png")
# elif condition_code == "sleet":
#     weather_ico = os.path.abspath("img/mixed_rain_snow.png")
# elif condition_code == "snow":
#     weather_ico = os.path.abspath("img/showers_snow.png")
# elif condition_code == "light-snow":
#     weather_ico = os.path.abspath("img/cloudy_with_snow.png")
# elif condition_code == "heavy-snow":
#     weather_ico = os.path.abspath("img/heavy_snow.png")
# else:
#     weather_ico = os.path.abspath("img/not_available.png")
#
# weather_info_top = (
#     f"{temp_now}°C "
#     f"feels like: {temp_feel}°C"
# )
# weather_city = (
#     f"{location}"
# )
# weather_info_left = (
#     f"Vėjo greitis: {wind_speed} m/s\n"
#     f"Vėjo gūsiai: {wind_gust} m/s\n"
#     f"Vėjo kryptis: {wind_degree}° {wind_direction}\n"
#     f"Debesuotumas: {cloud_cover}%"
# )
# weather_info_right = (
#     f"Slėgis: {pressure_hpa} hPa, {pressure_mmhg:.0f} mmHg(Torr)\n"
#     f"Drėgmė: {relative_humidity}%\n"
#     f"Krituliai: {total_precipitation} mm\n"
#     f"Oras: {condition_code}"
# )
# print(weather_city, weather_info_top, weather_info_left, weather_info_right, "\n", "-"*70)

# ------------------ def kad veiktų atnaujinimas(timer) ----------------------------

# import json
# import os
# import requests
#
#
# def get_weather_data(place="žiegždriai"):
#     url = f"https://api.meteo.lt/v1/places/{place}/forecasts/long-term"
#     response = requests.get(url)
#     data = response.json()
#     print(json.dumps(data, indent=4))
#
#     forecast = data["forecastTimestamps"][0]
#     time_utc = forecast["forecastTimeUtc"]
#     location = data["place"]["name"]
#     temp_now = forecast["airTemperature"]
#     temp_feel = forecast["feelsLikeTemperature"]
#     wind_speed = forecast["windSpeed"]
#     wind_gust = forecast["windGust"]
#     wind_degree = forecast["windDirection"]
#     cloud_cover = forecast["cloudCover"]
#     pressure_hpa = forecast["seaLevelPressure"]
#     hpa_to_mmhg = 0.75006
#     pressure_mmhg = pressure_hpa * hpa_to_mmhg
#     relative_humidity = forecast["relativeHumidity"]
#     total_precipitation = forecast["totalPrecipitation"]
#     condition_code = forecast["conditionCode"]
#     print(forecast)
#     print(time_utc)
#
#     if 350 <= wind_degree < 10:
#         wind_direction = 'N'
#     elif 10 <= wind_degree < 80:
#         wind_direction = 'NE'
#     elif 80 <= wind_degree < 100:
#         wind_direction = 'E'
#     elif 100 <= wind_degree < 170:
#         wind_direction = 'SE'
#     elif 170 <= wind_degree < 190:
#         wind_direction = 'S'
#     elif 190 <= wind_degree < 260:
#         wind_direction = 'SW'
#     elif 260 <= wind_degree < 280:
#         wind_direction = 'W'
#     else:
#         wind_direction = 'NW'
#
#     weather_ico = ""
#     if condition_code == "cloudy":
#         weather_ico = os.path.abspath("img/cloudy.png")
#     elif condition_code == "partly-cloudy":
#         weather_ico = os.path.abspath("img/mostly_clear_day.png")
#     elif condition_code == "clear":
#         weather_ico = os.path.abspath("img/clear_day.png")
#     elif condition_code == "light-rain":
#         weather_ico = os.path.abspath("img/drizzle.png")
#     elif condition_code == "rain":
#         weather_ico = os.path.abspath("img/showers_rain.png")
#     elif condition_code == "heavy-rain":
#         weather_ico = os.path.abspath("img/heavy_rain.png")
#     elif condition_code == "sleet":
#         weather_ico = os.path.abspath("img/mixed_rain_snow.png")
#     elif condition_code == "snow":
#         weather_ico = os.path.abspath("img/showers_snow.png")
#     elif condition_code == "light-snow":
#         weather_ico = os.path.abspath("img/cloudy_with_snow.png")
#     elif condition_code == "heavy-snow":
#         weather_ico = os.path.abspath("img/heavy_snow.png")
#     else:
#         weather_ico = os.path.abspath("img/not_available.png")
#
#     weather_info_top = f"{temp_now}°C feels like: {temp_feel}°C"
#     weather_city = f"{location}"
#     weather_info_left = f"Vėjo greitis: {wind_speed} m/s\nVėjo gūsiai: {wind_gust} m/s\nVėjo kryptis: {wind_degree}° {wind_direction}\nDebesuotumas: {cloud_cover}%"
#     weather_info_right = f"Slėgis: {pressure_hpa} hPa, {pressure_mmhg:.0f} mmHg(Torr)\nDrėgmė: {relative_humidity}%\nKrituliai: {total_precipitation} mm\nOras: {condition_code}"
#
#     return weather_city, weather_info_top, weather_info_left, weather_info_right, weather_ico

# -------------- Atnaujintas prognozės pasirinkimas su -3 val. --------------------------

import json
import os
import requests
from datetime import datetime



def get_weather_data(place="kaunas"):
    url = f"https://api.meteo.lt/v1/places/{place}/forecasts/long-term"
    response = requests.get(url)
    data = response.json()

    # Gauti visus prognozės laikus
    forecast_datetimes = [
        datetime.strptime(forecast["forecastTimeUtc"], "%Y-%m-%d %H:%M:%S")
        for forecast in data["forecastTimestamps"]
    ]

    # Dabartinis laikas
    current_time = datetime.utcnow()
    print("-" * 50, "\nDabartinis Grinvičo laikas", current_time, "UTC")

    # Rasti prognozę, kuri atitinka dabartinį laiką
    valid_forecasts = [
        forecast for i, forecast in enumerate(data["forecastTimestamps"])
        if forecast_datetimes[i] <= current_time
    ]

    if not valid_forecasts:
        print("Nėra galiojančios prognozės šiam laikui.")
        return None

    forecast = valid_forecasts[-1]
    time_utc = forecast["forecastTimeUtc"]
    location = data["place"]["name"]
    temp_now = forecast["airTemperature"]
    temp_feel = forecast["feelsLikeTemperature"]
    wind_speed = forecast["windSpeed"]
    wind_gust = forecast["windGust"]
    wind_degree = forecast["windDirection"]
    cloud_cover = forecast["cloudCover"]
    pressure_hpa = forecast["seaLevelPressure"]
    hpa_to_mmhg = 0.75006
    pressure_mmhg = pressure_hpa * hpa_to_mmhg
    relative_humidity = forecast["relativeHumidity"]
    total_precipitation = forecast["totalPrecipitation"]
    condition_code = forecast["conditionCode"]

    print("JSON info\n", forecast)
    print("-" * 50)

    # Vėjo krypties nustatymas su žodynu
    wind_direction_dict = {
        range(350, 360): 'N', range(0, 10): 'N',
        range(10, 80): 'NE', range(80, 100): 'E',
        range(100, 170): 'SE', range(170, 190): 'S',
        range(190, 260): 'SW', range(260, 280): 'W',
        range(280, 350): 'NW'
    }
    wind_direction = next(
        (dir for deg_range, dir in wind_direction_dict.items() if wind_degree in deg_range),
        'Unknown'
    )

    # Paveikslėlio nustatymas pagal oro sąlygas
    weather_icons = {
        "cloudy": "cloudy.png", "partly-cloudy": "mostly_clear_day.png",
        "clear": "clear_day.png", "light-rain": "drizzle.png",
        "rain": "showers_rain.png", "heavy-rain": "heavy_rain.png",
        "sleet": "mixed_rain_snow.png", "snow": "showers_snow.png",
        "light-snow": "cloudy_with_snow.png", "heavy-snow": "heavy_snow.png"
    }
    weather_ico = os.path.abspath(f"img/{weather_icons.get(condition_code, 'not_available.png')}")

    weather_info_top = f"{temp_now}°C feels like: {temp_feel}°C"
    weather_city = f"{location}"
    weather_info_left = f"Vėjo greitis: {wind_speed} m/s\nVėjo gūsiai: {wind_gust} m/s\nVėjo kryptis: {wind_degree}° {wind_direction}\nDebesuotumas: {cloud_cover}%"
    weather_info_right = f"Slėgis: {pressure_hpa} hPa, {pressure_mmhg:.0f} mmHg(Torr)\nDrėgmė: {relative_humidity}%\nKrituliai: {total_precipitation} mm\nOras: {condition_code}"

    return weather_city, weather_info_top, weather_info_left, weather_info_right, weather_ico
