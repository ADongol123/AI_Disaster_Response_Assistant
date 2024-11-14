import requests
import csv
from datetime import datetime
import pandas as pd
import os

# Read the CSV file containing states with their latitudes and longitudes
cities = pd.read_csv("../data/us_states_lat_long.csv")  # Assuming the CSV has columns 'City', 'Latitude', 'Longitude'
print(cities.columns)

# NOAA NWS API URL for accessing points
base_url = "https://api.weather.gov/points/"

# Define the folder where the file will be saved
folder_name = "../data"  # Folder where the CSV will be saved (you want to use "data" folder)

# Check if the folder exists. If it doesn't, it will be created.
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Path to save the CSV file
filename = os.path.join(folder_name, "us_weather_forecast.csv")

# Open CSV file to write data
with open(filename, mode="a", newline="") as file:  # Open in append mode to add to the file if it exists
    writer = csv.writer(file)

    # If the file is empty, write the header
    if file.tell() == 0:  # Check if the file is empty by checking the cursor position
        writer.writerow([
            "City", "Date", "Start Time", "End Time", "Temperature", "Temperature Unit", "Wind Speed", "Wind Direction",
            "Short Forecast", "Detailed Forecast", "Humidity", "Precipitation Amount", "Pressure", "UV Index",
            "Dew Point", "Cloud Cover", "Wind Gust Speed", "Visibility", "Icon Link", "Alert Event", "Alert Severity",
            "Alert Certainty", "Alert Urgency", "Alert Area Description", "Alert Instructions"
        ])

    # Iterate through each city in the DataFrame
    for index, city in cities.iterrows():
        latitude = city["Latitude"]
        longitude = city["Longitude"]
        city_name = city["Capital City"]
        state = city["State"]

        # Get the forecast URL for the specified location
        location_url = f"{base_url}{latitude},{longitude}"

        try:
            # Fetch the forecast office and grid points for the location
            response = requests.get(location_url)
            response.raise_for_status()  # Check for request errors
            data = response.json()

            # Extract forecast URL
            forecast_url = data["properties"]["forecast"]

            # Fetch the weather forecast data
            forecast_response = requests.get(forecast_url)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # Check if there are alerts for the location
            alert_url = data["properties"].get("alert", None)
            alert_event, alert_severity, alert_certainty, alert_urgency = "N/A", "N/A", "N/A", "N/A"
            alert_area_description, alert_instructions = "N/A", "N/A"

            if alert_url:
                alert_response = requests.get(alert_url)
                alert_response.raise_for_status()
                alert_data = alert_response.json()

                # Extracting alert details if available
                if "features" in alert_data:
                    for alert in alert_data["features"]:
                        alert_event = alert["properties"].get("event", "N/A")
                        alert_severity = alert["properties"].get("severity", "N/A")
                        alert_certainty = alert["properties"].get("certainty", "N/A")
                        alert_urgency = alert["properties"].get("urgency", "N/A")
                        alert_area_description = alert["properties"].get("areaDescription", "N/A")
                        alert_instructions = alert["properties"].get("instruction", "N/A")

            # Loop through forecast periods and write data to CSV
            for period in forecast_data["properties"]["periods"]:
                writer.writerow([
                    city_name, datetime.now().strftime('%Y-%m-%d'), period["startTime"], period["endTime"],
                    period["temperature"], period["temperatureUnit"], period["windSpeed"], period["windDirection"],
                    period["shortForecast"], period["detailedForecast"], period.get("humidity", "N/A"),
                    period.get("precipitationAmount", "N/A"), period.get("pressure", "N/A"),
                    period.get("uvIndex", "N/A"),
                    period.get("dewPoint", "N/A"), period.get("cloudCover", "N/A"), period.get("gustSpeed", "N/A"),
                    period.get("visibility", "N/A"), period["icon"], alert_event, alert_severity, alert_certainty,
                    alert_urgency, alert_area_description, alert_instructions
                ])

            print(f"Weather data for {city_name} has been saved.")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {city_name}: {e}")

print(f"Weather data for the selected cities has been saved to {filename}")
