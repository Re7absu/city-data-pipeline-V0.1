import os
from dotenv import load_dotenv
import requests
import time
from pathlib import Path
from datetime import datetime
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)


raw_dir = Path("./data/raw")

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Check if the API key is loaded
print("API key loaded:", bool(WEATHER_API_KEY))


base_url = "https://api.weatherapi.com/v1/current.json"
cities = [
    "Riyadh",
    "Jeddah",
    "Dammam",
    "Makkah",
    "Madinah",
    "Abha",
    "Tabuk",
    "Hail",
    "Jazan",
    "Buraidah",
]

@retry(
    retry=retry_if_exception_type(
        (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        )
    ),
    wait=wait_exponential(
        multiplier=1,
        min=1,
        max=10,
    ),
    stop=stop_after_attempt(3),
    reraise=True,
)

def get_weather(city):
    params = {"key": WEATHER_API_KEY, "q": city, "aqi": "yes"}
    response = requests.get(base_url, params=params, timeout=15)
    # raise_for_status(): Raises an HTTPError for unsuccessful HTTP responses.
    response.raise_for_status()
    return response


def main():
    if not WEATHER_API_KEY:
        raise ValueError("Weather API KEY is missing")

    ## Create the date folder once
    date_folder = raw_dir / datetime.now().strftime("%Y-%m-%d")
    date_folder.mkdir(parents=True, exist_ok=True)
    

    for city in cities:
        try:
             
            response = get_weather(city)
           
            # Save raw response before processing
            timestamp = datetime.now().strftime("%H-%M-%S")
            filename = f"{city.lower()}_{timestamp}.json"
            file_path = date_folder / filename
            file_path.write_bytes( response.content)
            print(f"Saved: {file_path}")

           

            ## Process the response after saving
            data = response.json()
            city_name = data["location"]["name"]
            temperature = data["current"]["temp_c"]
            humidity = data["current"]["humidity"]
            wind_speed = data["current"]["wind_kph"]
            air_quality = data["current"]["air_quality"]
            pm2_5 = air_quality["pm2_5"]
            pm10 = air_quality["pm10"]

            # Parse the response after saving the raw data
            print(f"{city_name} : " f"Temperature = {temperature}°C, " f"Humidity = {humidity}%")
            time.sleep(1)

         

        except requests.exceptions.RequestException as error:
            print(f"Failed to fetch {city}: {error}")

if __name__ == "__main__":
    main()
