import os, sys, requests, logging
from datetime import datetime, timezone
from config import LOCATION as default_location

WIND_DIRECTIONS = [
    (0, 10, 'N'), (10, 80, 'NE'), (80, 100, 'E'),
    (100, 170, 'SE'), (170, 190, 'S'), (190, 260, 'SW'),
    (260, 280, 'W'), (280, 350, 'NW'), (350, 360, 'N'),
]

CONDITION_NAMES_LT = {
    "clear": "Giedra",
    "partly-cloudy": "Mažai debesuota",
    "cloudy-with-sunny-intervals": "Debesuota su pragiedruliais",
    "cloudy": "Debesuota",
    "light-rain": "Nedidelis lietus",
    "rain": "Lietus",
    "heavy-rain": "Smarkus lietus",
    "thunder": "Perkūnija",
    "isolated-thunderstorms": "Trumpas lietus su perkūnija",
    "thunderstorms": "Lietus su perkūnija",
    "heavy-rain-with-thunderstorms": "Smarkus lietus su perkūnija",
    "light-sleet": "Nedidelė šlapdriba",
    "sleet": "Šlapdriba",
    "freezing-rain": "Lijundra",
    "hail": "Kruša",
    "light-snow": "Nedidelis sniegas",
    "snow": "Sniegas",
    "heavy-snow": "Smarkus sniegas",
    "fog": "Rūkas",
}

WEATHER_ICONS = {
    "clear": "clear_day.png",
    "partly-cloudy": "mostly_clear_day.png",
    "cloudy-with-sunny-intervals": "mostly_cloudy_day.png",
    "cloudy": "cloudy.png",
    "light-rain": "drizzle.png",
    "rain": "showers_rain.png",
    "heavy-rain": "heavy_rain.png",
    "thunder": "thunder.png",
    "isolated-thunderstorms": "isolated_thunderstorms.png",
    "thunderstorms": "thunderstorms.png",
    "heavy-rain-with-thunderstorms": "heavy_rain_thunderstorms.png",
    "light-sleet": "light_sleet.png",
    "sleet": "mixed_rain_snow.png",
    "freezing-rain": "freezing_rain.png",
    "hail": "hail.png",
    "light-snow": "cloudy_with_snow.png",
    "snow": "showers_snow.png",
    "heavy-snow": "heavy_snow.png",
    "fog": "haze_fog_dust_smoke.png",
}

HPA_TO_MMHG = 0.75006


def _base_path():
    # PyInstaller exe atveju naudoja _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_wind_direction(degrees: int) -> str:
    for low, high, label in WIND_DIRECTIONS:
        if low <= degrees < high:
            return label
    return "N"


def get_forecast_step_hours(timestamps: list) -> int:
    """Nustato prognozės laiko žingsnį valandomis."""
    if len(timestamps) >= 2:
        t1 = datetime.strptime(timestamps[0]["forecastTimeUtc"], "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime(timestamps[1]["forecastTimeUtc"], "%Y-%m-%d %H:%M:%S")
        return int((t2 - t1).total_seconds() // 3600)
    return 1


def get_weather_data(place: str = default_location) -> tuple | None:
    logging.info(f"Meteo_lt: Užklausa vietai '{place}'")
    try:
        url = f"https://api.meteo.lt/v1/places/{place}/forecasts/long-term"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logging.error(f"Meteo_lt: Ryšio klaida: {e}")
            return None

        timestamps = data.get("forecastTimestamps", [])
        if not timestamps:
            logging.error("Meteo_lt: Prognozės duomenų nėra.")
            return None

        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        forecast = min(
            timestamps,
            key=lambda f: abs(
                datetime.strptime(f["forecastTimeUtc"], "%Y-%m-%d %H:%M:%S") - current_time
            )
        )

        logging.info(f"Meteo_lt: Parinkta prognozė laikui {forecast['forecastTimeUtc']}")

        step_hours = get_forecast_step_hours(timestamps)
        total_precipitation = forecast["totalPrecipitation"]
        precipitation_per_hour = total_precipitation / step_hours if step_hours > 0 else total_precipitation

        city = data["place"]["name"]
        temp_now = forecast["airTemperature"]
        temp_feel = forecast["feelsLikeTemperature"]
        wind_speed = forecast["windSpeed"]
        wind_gust = forecast["windGust"]
        wind_degree = forecast["windDirection"]
        cloud_cover = forecast["cloudCover"]
        pressure_hpa = forecast["seaLevelPressure"]
        pressure_mmhg = pressure_hpa * HPA_TO_MMHG
        relative_humidity = forecast["relativeHumidity"]
        condition_code = forecast["conditionCode"]

        wind_direction = get_wind_direction(int(wind_degree))
        icon_file = WEATHER_ICONS.get(condition_code, "not_available.png")
        weather_ico = os.path.join(_base_path(), "img", icon_file)

        weather_info_top = f"{temp_now}°C"
        weather_feels = f"feels like: {temp_feel}°C"
        weather_info_left = (
            f"Vėjo greitis: {wind_speed} m/s\n"
            f"Vėjo gūsiai: {wind_gust} m/s\n"
            f"Vėjo kryptis: {wind_degree}° {wind_direction}\n"
            f"Debesuotumas: {cloud_cover}%"
        )
        weather_info_right = (
            f"Slėgis: {pressure_hpa} hPa, {pressure_mmhg:.0f} mmHg\n"
            f"Drėgmė: {relative_humidity}%\n"
            f"Krituliai: {precipitation_per_hour:.2f} mm/val\n"
            f"Oras: {CONDITION_NAMES_LT.get(condition_code, 'Nenustatyta')}"
        )

        logging.info("Meteo_lt: Duomenys sėkmingai suformuoti")
        return city, weather_info_top, weather_feels, weather_info_left, weather_info_right, weather_ico

    except Exception as e:
        logging.error(f"Meteo_lt: Nenumatyta klaida: {e}", exc_info=True)
        return None