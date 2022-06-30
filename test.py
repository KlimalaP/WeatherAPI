from flask import Flask, render_template, request
import requests
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

name = ''


@app.route('/temperature', methods=['POST'])
def temperature():
    zipcode = request.form['zip']
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?zip='+zipcode+',pl&appid=b763e03c10b72e7ba2d23d11bed70811')
    json_object = r.json()
    temp_k = float(json_object['main']['temp'])
    temp_c = temp_k - 273.15
    pres = int(json_object['main']['pressure'])
    name = str(json_object['name'])
    description = json_object['weather'][0]['description']
    vel = float(json_object['wind']['speed'])
    icon_code = json_object['weather'][0]['icon']
    return render_template('temperature.html', temp=round(temp_c), press=pres, windVelocity=vel, city=name,
                           weatherDescription=str(description), idk=json_object, icon_code=icon_code)


def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png',
                bbox_inches='tight')
    img.seek(0)
    return base64.b64encode(img.getvalue())


@app.route('/temperature/forecast', methods=['POST'])
def forecast():
    forecast_list = []
    date = []
    r = requests.get('http://api.openweathermap.org/data/2.5/forecast?q='+name+',pl&appid=b763e03c10b72e7ba2d23d11bed70811')
    json_object = r.json()

    for_how_long = 0
    for i in range(0, 16):
        forecast_list.append((json_object['list'][i]['main']['temp'])-273.15)
        date.append(json_object['list'][i]['dt_txt'])
        for_how_long += 1
    s = pd.Series(forecast_list, date)
    fig, ax = plt.subplots()
    s.plot.bar()
    ax.set_facecolor('#ADD8E6')
    fig.savefig('forecast.png')
    return render_template('forecast.html', ans='<img src="data:image/png;base64, {}">'.format(fig_to_base64(fig).decode('utf-8')), length_of_forecast=for_how_long*3)

#ctrl+shift+r czyszczenia cache przegladarki w przypadku problemu z wykresem


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
