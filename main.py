import streamlit as st
import pandas as pd
import plotly.express as px
import pandas as pd
import requests

data = []
selected_columns = []
month_names = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzieńeń']
years = [2022, 2023, 2024, 2025]
wszystkie_miasta = ['Kraków', 'Katowice', 'Zakopane']
columns_labels = {
    'Kraków': 'Kraków - Aleja Krasińskiego (pył zawieszony PM10 [jednostka ug/m3])',
    'Zakopane': 'Zakopane - ul. Sienkiewicza (pył zawieszony PM10 [jednostka ug/m3])',
    'Katowice': 'Katowice - ul. Kossutha (pył zawieszony PM10 [jednostka ug/m3])'
}

weather_codes = {
    0: "☀️ Bezchmurne niebo",
    1: "🌤️ Przeważnie bezchmurnie",
    2: "⛅ Częściowe zachmurzenie",
    3: "☁️ Całkowite zachmurzenie",
    45: "🌫️ Mgła",
    48: "🌫️❄️ Mgła z osadzającym się szronem",
    51: "🌦️ Mżawka: słaba",
    53: "🌦️ Mżawka: umiarkowana",
    55: "🌧️ Mżawka: gęsta",
    56: "🌧️❄️ Marznąca mżawka: słaba",
    57: "🌧️❄️ Marznąca mżawka: gęsta",
    61: "🌧️ Deszcz: niewielki",
    63: "🌧️ Deszcz: umiarkowany",
    65: "🌧️💧 Deszcz: silny",
    66: "🌧️❄️ Marznący deszcz: słaby",
    67: "🌧️❄️ Marznący deszcz: silny",
    71: "🌨️ Śnieg: niewielki",
    73: "🌨️ Śnieg: umiarkowany",
    75: "❄️🌨️ Śnieg: silny",
    77: "❄️ Ziarenka śniegu",
    80: "🌦️ Przelotne opady deszczu: lekkie",
    81: "🌧️ Przelotne opady deszczu: umiarkowane",
    82: "🌧️💦 Przelotne opady deszczu: intensywne",
    85: "🌨️ Przelotne opady śniegu: lekkie",
    86: "🌨️❄️ Przelotne opady śniegu: intensywne",
    95: "⛈️ Burza: lekka lub umiarkowana",
    96: "⛈️🌨️ Burza z lekkim gradem",
    99: "⛈️❄️ Burza z silnym gradem"
}

st.set_page_config(layout="wide")

#SIDEBAR
typOkresu = st.sidebar.selectbox("Wybierz okres", ['Rok', 'Miesiąc', 'Dowolny zakres'])
if typOkresu == 'Rok':
    okresRok = st.sidebar.selectbox("Wybierz rok", years)
elif typOkresu == 'Miesiąc':
    okresRok = st.sidebar.selectbox("Wybierz rok", years)
    okresMiesiac = st.sidebar.selectbox("Wybierz miesiąc", month_names)
elif typOkresu == 'Dowolny zakres':
    okresPoczatek = st.sidebar.date_input("Początek okresu", value=pd.to_datetime('2022-01-01')).strftime("%Y-%m-%d")
    okresKoniec = st.sidebar.date_input("Koniec okresu", value=pd.to_datetime('2025-04-30')).strftime("%Y-%m-%d")

st.title('Poziomy zanieczyszczeń PM10 dla wybranych miast Południowej Polski')
with st.container(border=True):
    miasta = st.multiselect("Miasta", wszystkie_miasta, default=wszystkie_miasta)


def setSelectedColumns():
    global selected_columns
    selected_columns = ['Data']
    for miasto in miasta:
        if miasto in wszystkie_miasta:
            selected_columns.append(columns_labels[miasto])
    selected_columns.sort()

def loadData():
    global data
    setSelectedColumns()
    dtype_dict = {    
                    'Kraków - Aleja Krasińskiego (pył zawieszony PM10 [jednostka ug/m3])': 'float',
                    'Zakopane - ul. Sienkiewicza (pył zawieszony PM10 [jednostka ug/m3])' : 'float',
                    'Katowice - ul. Kossutha (pył zawieszony PM10 [jednostka ug/m3])' : 'float'
}
    path = f'./gios-pjp-data_2022-2025.csv'
    df = pd.read_csv(path, sep=',', encoding='utf-8', na_values=['-', ' ', ''], index_col=False, dtype=dtype_dict, parse_dates=['Data'])

    if typOkresu == 'Miesiąc':
        temp_data = df[(df['Data'].dt.month == month_names.index(okresMiesiac)+1) & (df['Data'].dt.year == okresRok)]
        data = temp_data[selected_columns]
    elif typOkresu == 'Rok':
        temp_data = df[(df['Data'].dt.year == okresRok)]
        data = temp_data[selected_columns]
    elif typOkresu == 'Dowolny zakres':
        temp_data = df[(df['Data'] >= okresPoczatek) & (df['Data'] <= okresKoniec)]
        data = temp_data[selected_columns]

if st.sidebar.button("Pobierz dane", key="pobierz_dane"):
    loadData()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Dopuszczalne średnie dobowe stężenie PM10:", value='50 µg/m³')
    if (type(data) == pd.DataFrame) and (not data.empty):
        mean = data.select_dtypes(include='float64').mean().mean()
        st.metric(label="Średnia wartość PM10: ", value=round(mean,2))

        dni_powyzej_poziomu = data[data.iloc[:, 1:] > 50].count().sum()
        st.metric(label="Ilość dni z przekroczoną normą PM10:", value=dni_powyzej_poziomu)
with col2:
    st.metric(label="Poziom informowania", value='100 µg/m³')
    if (type(data) == pd.DataFrame) and (not data.empty):
        max_val = data.select_dtypes(include='float64').max().max()
        st.metric(label="(MAX) Najwyższa wartość PM10: ", value=max_val)

        dni_powyzej_poziomu = data[data.iloc[:, 1:] > 100].count().sum()
        st.metric(label="Ilość dni z przekroczeniem poziomu informowania: ", value=dni_powyzej_poziomu)
with col3:
    st.metric(label="Poziom alarmowy:", value='150 µg/m³')
    if (type(data) == pd.DataFrame) and (not data.empty):
        min_val = data.select_dtypes(include='float64').min().min()
        st.metric(label="(MIN) Najniższa wartość PM10: ", value=min_val)

        dni_powyzej_poziomu = data[data.iloc[:, 1:] > 150].count().sum()
        st.metric(label="Ilość dni z przekroczeniem poziomu alarmowego:", value=dni_powyzej_poziomu)


#print data frame
if (type(data) == pd.DataFrame) and (not data.empty):
    tab1, tab2 = st.tabs(["Chart", "Dataframe"])
    tab1.line_chart(data, use_container_width=True, x='Data', y=selected_columns.remove('Data'))
    tab2.dataframe(data, use_container_width=True)
else:
    st.warning("Brak danych do wyświetlenia. Kliknij 'Pobierz dane' jeśli zmieniałeś/aś zakres danych.")

#weather data
pobierz_pogode = st.sidebar.checkbox("Pobierz historyczne dane pogodowe", key="pobierz_pogode", value=False)

def getWeatherData():
    start_date = ''
    end_date = ''

    if typOkresu == 'Miesiąc':
        start_date = f"{okresRok}-{month_names.index(okresMiesiac)+1:02d}-01"
        end_date = f"{okresRok}-{month_names.index(okresMiesiac)+1:02d}-31"
    elif typOkresu == 'Rok':
        start_date = f"{okresRok}-01-01"
        end_date = f"{okresRok}-12-31"
    elif typOkresu == 'Dowolny zakres':
        start_date = okresPoczatek
        end_date = okresKoniec

    # Lista współrzędnych dla miast
    lokalizacje = {
        'Kraków': (50.06143, 19.93658),
        'Katowice': (50.25841, 19.02754),
        'Zakopane': (49.2992, 19.9496)
    }

    all_data = []

    for miasto in miasta:
        if miasto in lokalizacje:
            lat, lon = lokalizacje[miasto]

            openMeteoUrl = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,wind_gusts_10m_max,weather_code&timezone=Europe%2FWarsaw"
            response = requests.get(openMeteoUrl, params="")
            if response.status_code == 200:
                json_data = response.json()
                if 'daily' in json_data:
                    df = pd.DataFrame(json_data['daily'])
                    df['Miasto'] = miasto
                    all_data.append(df)
            else:
                print(f"Błąd pobierania danych dla {miasto}: {response.status_code}")

    # Połącz wszystkie dane w jeden DataFrame
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()
    
#print data frame
if pobierz_pogode:
    weatherData = getWeatherData()
    if (type(weatherData) == pd.DataFrame) and (not weatherData.empty):
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Opis pogody", "Temperatura", "Suma opadów", "Prędkość wiatru oraz porywy", "Dataframe"])
        weatherData['weather_code'] = weatherData['weather_code'].map(weather_codes)
        tab1.dataframe(weatherData.pivot(index='Miasto', columns='time', values='weather_code'))
        for miasto in miasta:
            df_m = weatherData[weatherData['Miasto'] == miasto]
            # Tworzymy DataFrame z time jako index i dwiema kolumnami temperatur
            df_pivot = df_m.set_index('time')[['temperature_2m_max', 'temperature_2m_min']]
            # Wyświetlamy wykres w tab2 z tytułem
            tab2.write(f"Wykres temperatur dla: {miasto}")
            tab2.line_chart(df_pivot, color=["#FF0000", "#0000FF"])

            df_pivot2 = df_m.set_index('time')[['wind_speed_10m_max', 'wind_gusts_10m_max']]
            tab4.write(f"Wykres wiatru dla: {miasto} w km/h")
            tab4.line_chart(df_pivot2)

        # Pivot: indeks = data, kolumny = miasta, wartości = suma opadów
        pivot_df = weatherData.pivot(index='time', columns='Miasto', values='precipitation_sum').fillna(0)
        # Wyświetl wykres słupkowy
        tab3.bar_chart(pivot_df, stack=False)
        tab5.dataframe(weatherData)
    else:
        st.warning("Brak danych pogodowych do wyświetlenia. Sprawdź poprawność wyboru okresu lub miast.")