import streamlit as st
import pandas as pd

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

st.set_page_config(layout="wide")

#SIDEBAR
typOkresu = st.sidebar.selectbox("Wybierz okres", ['Rok', 'Miesiąc'])
if typOkresu == 'Rok':
    okresRok = st.sidebar.selectbox("Wybierz rok", years)
elif typOkresu == 'Miesiąc':
    okresRok = st.sidebar.selectbox("Wybierz rok", years)
    okresMiesiac = st.sidebar.selectbox("Wybierz miesiąc", month_names)

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
    path = f'./gios-pjp-data_{okresRok}.csv'
    df = pd.read_csv(path, sep=',', encoding='utf-8', na_values=['-'], index_col=False, dtype=dtype_dict, parse_dates=['Data'])

    if typOkresu == 'Miesiąc':
        temp_data = df[(df['Data'].dt.month == month_names.index(okresMiesiac)+1) & (df['Data'].dt.year == okresRok)]
        data = temp_data[selected_columns]
    elif typOkresu == 'Rok':
        data = df[selected_columns]

if st.sidebar.button("Pobierz dane", key="pobierz_dane"):
    loadData()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Dopuszczalne średnie dobowe stężenie PM10:", value='50 µg/m³')
    if (type(data) == pd.DataFrame) and (not data.empty):
        mean = data.select_dtypes(include='float64').mean().mean()
        st.metric(label="Średnia wartość PM10: ", value=round(mean,2))

        dni_powyzej_poziomu = data[data.iloc[:, 1:] > 50].count().sum()
        st.metric(label="Ilość dni z przekroczoną normą PM10:", value=int(dni_powyzej_poziomu))
with col2:
    st.metric(label="Poziom informowania po przekroczeniu śr. dobowego stężenia PM10:", value='100 µg/m³')
    if (type(data) == pd.DataFrame) and (not data.empty):
        max_val = data.select_dtypes(include='float64').max().max()
        st.metric(label="Najwyższa wartość PM10: ", value=max_val)

        dni_powyzej_poziomu = data[data.iloc[:, 1:] > 100].count().sum()
        st.metric(label="Ilość dni z przekroczeniem poziomu informowania: ", value=dni_powyzej_poziomu)
with col3:
    st.metric(label="Ilość dni z przekroczeniem poziomu alarmowego:", value='150 µg/m³')
    if (type(data) == pd.DataFrame) and (not data.empty):
        min_val = data.select_dtypes(include='float64').min().min()
        st.metric(label="Najniższa wartość PM10: ", value=min_val)

        dni_powyzej_poziomu = data[data.iloc[:, 1:] > 150].count().sum()
        st.metric(label="Ilość dni z przekroczeniem poziomu alarmowego:", value=dni_powyzej_poziomu)


#print data frame
if (type(data) == pd.DataFrame) and (not data.empty):
    tab1, tab2 = st.tabs(["Chart", "Dataframe"])
    tab1.line_chart(data, use_container_width=True, x='Data', y=selected_columns.remove('Data'))
    tab2.dataframe(data, use_container_width=True)
else:
    st.warning("Brak danych do wyświetlenia. Kliknij 'Pobierz dane' jeśli zmieniałeś/aś zakres danych.")
