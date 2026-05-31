from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction_text = None
    weather_info = None
    selected_city = None

    if request.method == 'POST':
      
        selected_city = request.form.get('city').strip()
        
        if selected_city:
            
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={selected_city}&count=1&format=json"
            
            try:
                geo_response = requests.get(geo_url).json()
                if 'results' in geo_response:
                    lat = geo_response['results'][0]['latitude']
                    lon = geo_response['results'][0]['longitude']
                  
                    resolved_city = geo_response['results'][0]['name']
                    country = geo_response['results'][0].get('country', '')
                    
                    
                    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,rain,cloud_cover,weather_code&timezone=auto"
                    weather_data = requests.get(weather_url).json()
                    
                    current = weather_data['current']
                    temp = current['temperature_2m']
                    humidity = current['relative_humidity_2m']
                    cloud = current['cloud_cover']
                    is_raining = current['rain']
                    weather_code = current['weather_code']
                    
                    weather_info = {
                        'temp': temp,
                        'humidity': humidity,
                        'cloud': cloud,
                        'resolved_name': f"{resolved_city}, {country}"
                    }
                    
                    
                    rain_codes = [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 85, 86]
                    
                    if weather_code in rain_codes or is_raining > 0:
                        prediction_text = "🌧️ HAAN! Is waqt ya aaj ke din baarish ke bohot heavy chances hain. Umbrella lekar niklein!"
                    elif humidity >= 75 and cloud >= 60:
                        prediction_text = "⛈️ CHANCES HIGH HAIN! Hawa mein nami (Humidity) aur badal dono bohot zyada hain, jaldi rain ho sakti hai."
                    elif humidity >= 55 and cloud >= 45:
                        prediction_text = "⛅ MAUSAM BAN RAHA HAI! Badal chaye rahenge, halki boondabaandi (drizzle) ho sakti hai."
                    else:
                        prediction_text = "☀️ NAHI! Aaj rain ke bilkul chances nahi hain. Mausam saaf rahega."
                else:
                    prediction_text = f"❌ '{selected_city}' naam ki koi city nahi mili. Kripya sahi naam daalein!"
            except Exception as e:
                prediction_text = f"❌ Server Error: Connection nahi ho paya. ({e})"

    return render_template('index.html', prediction=prediction_text, weather=weather_info, selected_city=selected_city)

if __name__ == '__main__':
    app.run(debug=True)
