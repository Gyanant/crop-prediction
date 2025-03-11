import requests
import matplotlib.pyplot as plt
import json
from datetime import datetime

# Your WeatherAPI key
api_key = "dbc03686b6a54847a46120302242510"

def get_weather_data(api_key, location, days):
    url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days={days}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def display_current_weather(weather_data, location):
    current_weather = weather_data["current"]
    print(f"\nWeather in {location}:")
    print(f"Temperature: {current_weather['temp_c']}°C, Humidity: {current_weather['humidity']}%, Wind: {current_weather['wind_kph']} kph")
    print(f"Condition: {current_weather['condition']['text']}")

    if "air_quality" in current_weather:
        print(f"Air Quality Index (AQI): {current_weather['air_quality']['us-epa-index']}")
    if "uv" in current_weather:
        print(f"UV Index: {current_weather['uv']}")

def display_forecast(weather_data):
    print("\nForecast:")
    forecast_days = weather_data["forecast"]["forecastday"]
    dates = [day["date"] for day in forecast_days]
    temps = [day["day"]["avgtemp_c"] for day in forecast_days]
    rain_mm = [day["day"]["totalprecip_mm"] for day in forecast_days]

    for day in forecast_days:
        print(f"{day['date']} - Avg Temp: {day['day']['avgtemp_c']}°C, Condition: {day['day']['condition']['text']}, Rain: {day['day']['totalprecip_mm']} mm")

    return dates, temps, rain_mm

def plot_weather_trends(dates, temps, rain_mm, save_plot=False):
    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.plot(dates, temps, 'o-', color='tab:red', label="Avg Temperature (°C)")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Avg Temperature (°C)", color='tab:red')
    ax1.tick_params(axis='y', labelcolor='tab:red')
    plt.xticks(rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(dates, rain_mm, 's-', color='tab:blue', label="Rainfall (mm)")
    ax2.set_ylabel("Rainfall (mm)", color='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:blue')

    fig.tight_layout()
    plt.title("Weather Trends")
    plt.grid()

    if save_plot:
        plt.savefig("weather_trends.png")
        print("Plot saved as 'weather_trends.png'")

    plt.show()

def save_forecast_to_file(weather_data, filename="forecast.json"):
    with open(filename, "w") as file:
        json.dump(weather_data, file, indent=4)
    print(f"Forecast saved to '{filename}'")

def get_annual_weather_data(api_key, location):
    today = datetime.now()
    year = today.year
    total_temperature = 0
    total_rainfall = 0
    months_counted = 0

    # Loop through the months of the current year
    for month in range(1, 13):  # From January (1) to December (12)
        date = f"{year}-{month:02d}-01"  # Use the first day of each month
        url = f"https://api.weatherapi.com/v1/history.json?key={api_key}&q={location}&dt={date}"

        response = requests.get(url)
        weather_data = response.json()

        # Check if the response is valid
        if "forecast" in weather_data and "forecastday" in weather_data["forecast"]:
            # Get average temperature for the month
            monthly_avg_temp = sum(day["day"]["avgtemp_c"] for day in weather_data["forecast"]["forecastday"]) / len(weather_data["forecast"]["forecastday"])
            total_temperature += monthly_avg_temp

            # Get total rainfall for the month using your method
            monthly_rainfall = sum(day["day"]["totalprecip_mm"] for day in weather_data["forecast"]["forecastday"])
            total_rainfall += monthly_rainfall

            # Count only months with recorded data
            if monthly_rainfall > 0 or monthly_avg_temp is not None:
                months_counted += 1
    # Calculate average temperature and rainfall
    if months_counted > 0:
        average_temperature = total_temperature / months_counted  # Calculate average based on counted months
        average_rainfall = total_rainfall / months_counted  # Calculate average based on counted months
        return average_temperature, average_rainfall * 70  # Multiply average rainfall by 70
    else:
        return None, None

# Main execution
location = input("Enter the location (e.g., city name or postal code): ")
days = input("Enter the number of forecast days (1 to 10): ")

try:
    days = int(days)
    if not (1 <= days <= 10):
        raise ValueError("Days must be between 1 and 10.")
except ValueError as e:
    print("Invalid input for days:", e)
else:
    weather_data = get_weather_data(api_key, location, days)
    if weather_data and "forecast" in weather_data:
        display_current_weather(weather_data, location)
        dates, temps, rain_mm = display_forecast(weather_data)

        # Ask user if they want to save the plot
        save_plot = input("Do you want to save the weather trend plot? (yes/no): ").strip().lower() == "yes"
        plot_weather_trends(dates, temps, rain_mm, save_plot=save_plot)

        # Option to save forecast data
        save_data = input("Do you want to save the forecast data to a file? (yes/no): ").strip().lower() == "yes"
        if save_data:
            save_forecast_to_file(weather_data)

        # Calculate and display yearly averages using WeatherAPI
        avg_temperature, avg_rainfall = get_annual_weather_data(api_key, location)
        if avg_temperature is not None:
            print(f"\nAverage Temperature in {location} for {datetime.now().year}: {avg_temperature:.2f} °C")
        else:
            print(f"No temperature data available for {datetime.now().year} in {location}.")

        if avg_rainfall is not None:
            print(f"Average Rainfall in {location} for {datetime.now().year}: {avg_rainfall:.2f} mm")  # Rainfall multiplied by 70
        else:
            print(f"No rainfall data available for {datetime.now().year} in {location}.")
    else:
        print("Error:", weather_data.get("error", {}).get("message", "Unknown error"))