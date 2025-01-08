import streamlit as st
from database.db import Database
import pandas as pd
import plotly.express as px
import time

db = Database()

def get_sensor_data(room_id, sensor_table, limit=100):
    """
    Holt die Sensor-Daten aus der entsprechenden Tabelle basierend auf der Raumnummer.
    
    :param room_id: Die ID des Raums.
    :param sensor_table: Die Tabelle, aus der die Daten abgefragt werden.
    :param limit: Die Anzahl der Datensätze, die abgefragt werden (Standard: 100).
    :return: Die Sensor-Daten oder eine leere Liste, falls ein Fehler auftritt.
    """
    try:
        if sensor_table == 'flame_sensor_data':
            query = f"SELECT timestamp, fire_detected FROM {sensor_table} WHERE room_id = ? ORDER BY timestamp DESC LIMIT ?"
        elif sensor_table == 'dht22_data':
            query = f"SELECT timestamp, temperature, humidity FROM {sensor_table} WHERE room_id = ? ORDER BY timestamp DESC LIMIT ?"
        elif sensor_table == 'gas_sensor_data':
            query = f"SELECT timestamp, ppm FROM {sensor_table} WHERE room_id = ? ORDER BY timestamp DESC LIMIT ?"
        elif sensor_table == 'light_sensor_data':
            query = f"SELECT timestamp, lux FROM {sensor_table} WHERE room_id = ? ORDER BY timestamp DESC LIMIT ?"
        else:
            st.error(f"Unbekannte Sensor-Tabelle: {sensor_table}")
            return []
        
        result = db.connection.execute(query, (room_id, limit)).fetchall()
        
        if not result:
            st.error(f"Keine Daten für Raum {room_id} und Sensor-Tabelle {sensor_table}.")
        
        return result
    
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")
        return []

def get_selected_room():
    """
    Funktion, um den Raum auszuwählen.
    Gibt den Namen des ausgewählten Raums zurück.
    """
    rooms = db.connection.execute("SELECT id, name FROM rooms").fetchall()
    if not rooms:
        st.warning("Es gibt keine verfügbaren Räume. Bitte erstellen Sie zuerst einen Raum unter ⚙️ Einstellungen.")
        return None

    room_names = [room_name for _, room_name in rooms]
    selected_room_name = st.selectbox("Raum auswählen", room_names)
    
    return selected_room_name

def get_sensor_metric(sensor_table, room_id):
    """
    Holt den aktuellen Wert und den vorherigen Wert für einen bestimmten Sensor und berechnet die Differenz.
    
    :param sensor_table: Die Tabelle des Sensors (z.B. 'dht22_data' für Temperatur oder Luftfeuchtigkeit).
    :param room_id: Die ID des Raums.
    :return: Der aktuelle Wert, der vorherige Wert und die Differenz.
    """
    # Holen der letzten beiden Werte
    sensor_data = get_sensor_data(room_id, sensor_table, limit=2)
    
    if len(sensor_data) < 2:
        return None, None, None
    
    current_value = sensor_data[0]
    previous_value = sensor_data[1]
    
    # Berechne die Differenz
    if sensor_table == 'dht22_data':
        temperature_diff = current_value[1] - previous_value[1]
        humidity_diff = current_value[2] - previous_value[2]
        return (current_value[1], temperature_diff), (current_value[2], humidity_diff)
    elif sensor_table == 'light_sensor_data':
        lux_diff = current_value[1] - previous_value[1]
        return current_value[1], lux_diff
    elif sensor_table == 'gas_sensor_data':
        ppm_diff = current_value[1] - previous_value[1]
        return current_value[1], ppm_diff
    return None, None, None

def show_sensor_metrics(room_id):
    """
    Zeigt die Metriken für Temperatur, Luftfeuchtigkeit, Lichtintensität und Gas an und vergleicht sie mit den vorherigen Werten.
    """ 
    # 4 Spalten für Metriken erstellen
    st.write("")
    col1, col2, col3, col4 = st.columns(4)

    temp, temp_diff = get_sensor_metric('dht22_data', room_id)[0]
    if temp is not None:
        col1.metric("Temperatur (°C)", f"{temp:.1f}", f"{temp_diff:.1f}°", delta_color="normal")

    humidity, humidity_diff = get_sensor_metric('dht22_data', room_id)[1]
    if humidity is not None:
        col2.metric("Luftfeuchtigkeit (%)", f"{humidity:.1f}", f"{humidity_diff:.1f}%", delta_color="normal")

    lux, lux_diff = get_sensor_metric('light_sensor_data', room_id)
    if lux is not None:
        col3.metric("Lichtintensität (Lux)", f"{lux:.1f}", f"{lux_diff:.1f}", delta_color="normal")

    ppm, ppm_diff = get_sensor_metric('gas_sensor_data', room_id)
    if ppm is not None:
        col4.metric("Gas (ppm)", f"{ppm:.1f}", f"{ppm_diff:.1f}", delta_color="normal")

    st.write("")

def get_even_spacing_for_sections(amount_of_spaces=None):
    if amount_of_spaces is None:
        for i in range(3):
            st.write("")
    else:
        for i in range(amount_of_spaces):
            st.write("")

def refresh_data():
    """
    Holt die neuesten Daten und sorgt dafür, dass die Seite alle 60 Sekunden aktualisiert wird.
    """
    while True:
        time.sleep(60)
        st.rerun()

def show_sensor_data_line_chart_limit(room_id):
    """
    Zeigt die Sensor-Daten als Liniendiagramm an, basierend auf der Raumauswahl, dem Sensor und dem Limit.
    """
    room_name = db.get_room_name_by_id(room_id)
    st.subheader(f"🗂️ Sensor-Daten für Raum: {room_name}")

    sensor_option = st.selectbox("Sensor auswählen", ["Temperatur", "Luftfeuchtigkeit", "Lichtintensität", "Feuer", "Gas"])

    sensor_mapping = {
        "Temperatur": ("dht22_data", "temperature", "Temperatur (°C)"),
        "Luftfeuchtigkeit": ("dht22_data", "humidity", "Luftfeuchtigkeit (%)"),
        "Lichtintensität": ("light_sensor_data", "lux", "Lichtintensität (Lux)"),
        "Feuer": ("flame_sensor_data", "fire_detected", "Feuer erkannt"),
        "Gas": ("gas_sensor_data", "ppm", "Gaskonzentration (ppm)")
    }

    if sensor_option not in sensor_mapping:
        st.error("Ungültiger Sensor ausgewählt.")
        return

    sensor_table, value_column, y_label = sensor_mapping[sensor_option]

    # Maximale Anzahl der Datensätze für den ausgewählten Sensor aus der Datenbank holen
    max_records_query = f"SELECT COUNT(*) FROM {sensor_table} WHERE room_id = ?"
    try:
        max_records = db.connection.execute(max_records_query, (room_id,)).fetchone()[0]
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Datensatzanzahl: {e}")
        return

    # Slider für die Anzahl der Datensätze
    limit = st.slider(
        "Anzahl der anzuzeigenden Datensätze",
        min_value=1,
        max_value=max_records,
        value=min(100, max_records),  # Standardwert ist 100 oder weniger, falls weniger Datensätze vorhanden sind
        step=1
    )

    sensor_data = get_sensor_data(room_id, sensor_table, limit)

    if not sensor_data:
        st.warning(f"Keine Daten für den Sensor {sensor_option}.")
        return

    # Daten in DataFrame umwandeln
    if sensor_table == 'dht22_data':
        df = pd.DataFrame(sensor_data, columns=['timestamp', 'temperature', 'humidity'])
    elif sensor_table == 'flame_sensor_data':
        df = pd.DataFrame(sensor_data, columns=['timestamp', 'fire_detected'])
    elif sensor_table == 'gas_sensor_data':
        df = pd.DataFrame(sensor_data, columns=['timestamp', 'ppm'])
    elif sensor_table == 'light_sensor_data':
        df = pd.DataFrame(sensor_data, columns=['timestamp', 'lux'])

    # Zeitstempel umwandeln und leere DataFrame überprüfen
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    if df.empty:
        st.warning("Keine Daten zum Anzeigen.")
        return

    # Plotly-Diagramm erstellen
    fig = px.line(
        df, 
        x='timestamp', 
        y=value_column, 
        title=f"{sensor_option} über die Zeit",
        labels={'timestamp': 'Zeit', value_column: y_label},
        markers=True
    )
    
    # Diagramm in der App anzeigen
    st.plotly_chart(fig, use_container_width=True)

def show_area_graph_with_filters(room_id):
    """
    Zeigt einen Area-Graph mit Sensor- und Datumsauswahl an, wobei die Felder neben dem Graphen angeordnet sind.
    :param room_id: Die ID des Raums.
    """
    st.header("📅 Graph mit genauer Datumsauswahl")
    # Layout: Spalten für Felder und Graphen
    col1, col2 = st.columns([1, 2])

    with col1:
        sensor_option = st.selectbox(
            "Sensor zum Vergleich auswählen",
            ["Temperatur", "Luftfeuchtigkeit", "Lichtintensität", "Feuer", "Gas"],
            key="sensor_selectbox_key"
        )

    sensor_mapping = {
        "Temperatur": ("dht22_data", "temperature", "Temperatur (°C)"),
        "Luftfeuchtigkeit": ("dht22_data", "humidity", "Luftfeuchtigkeit (%)"),
        "Lichtintensität": ("light_sensor_data", "lux", "Lichtintensität (Lux)"),
        "Feuer": ("flame_sensor_data", "fire_detected", "Feuer erkannt"),
        "Gas": ("gas_sensor_data", "ppm", "Gaskonzentration (ppm)")
    }

    if sensor_option not in sensor_mapping:
        col1.error("Ungültiger Sensor ausgewählt.")
        return

    sensor_table, value_column, y_label = sensor_mapping[sensor_option]
    sensor_data = get_sensor_data(room_id, sensor_table, limit=100000)

    if not sensor_data:
        col1.warning("Keine Sensordaten verfügbar.")
        return

    # Daten in DataFrame laden
    if sensor_table == 'dht22_data':
        df = pd.DataFrame(sensor_data, columns=['timestamp', 'temperature', 'humidity'])
    elif sensor_table == 'flame_sensor_data':
        df = pd.DataFrame(sensor_data, columns=['timestamp', 'fire_detected'])
    elif sensor_table == 'gas_sensor_data':
        df = pd.DataFrame(sensor_data, columns=['timestamp', 'ppm'])
    elif sensor_table == 'light_sensor_data':
        df = pd.DataFrame(sensor_data, columns=['timestamp', 'lux'])

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date  # Nur das Datum extrahieren
    available_dates = df['date'].drop_duplicates().sort_values()

    with col1:
        # Auswahl der Anzahl der Tage
        num_days = st.number_input(
            "Anzahl der letzten Tage auswählen:",
            min_value=1,
            max_value=len(available_dates),  # Setze max_value auf die Anzahl der verfügbaren Tage
            value=1,  # Standardwert auf 1 Tag setzen
            key="num_days_input_key"
        )

        # Die letzten `num_days` Tage automatisch auswählen
        selected_dates = available_dates[-num_days:]

        # Mehrere Tage zur Auswahl anzeigen
        selected_dates = st.multiselect(
            "Verfügbare Tage auswählen:",
            options=available_dates,
            default=selected_dates,  # Die automatisch ausgewählten Tage als Standard
            key="date_multiselect_key"
        )

    # Daten nach den ausgewählten Tagen filtern
    filtered_df = df[df['date'].isin(selected_dates)]

    with col2:
        if not filtered_df.empty:
            # Spalte 'value' dynamisch erstellen basierend auf dem ausgewählten Sensor
            filtered_df['value'] = filtered_df[value_column]  # 'value' auf den Wert des gewählten Sensors setzen

            # Area-Graph anzeigen
            fig = px.area(
                filtered_df,
                x='timestamp',
                y='value',
                labels={'value': y_label, 'timestamp': 'Zeitpunkt'},
                markers=True
            )
            st.plotly_chart(fig)
        else:
            st.warning("Keine Daten für die ausgewählten Tage.")

def show_sensor_heatmap(room_id):
    """
    Zeigt eine interaktive Heatmap der Sensorwerte an, die über verschiedene Sensoren und Zeiträume hinweg aggregiert sind.
    
    :param room_id: Die ID des Raums, für den die Heatmap erstellt werden soll.
    """
    sensor_data = {
        'Temperatur': get_sensor_data(room_id, 'dht22_data', limit=100000),
        'Luftfeuchtigkeit': get_sensor_data(room_id, 'dht22_data', limit=100000),
        'Lichtintensität': get_sensor_data(room_id, 'light_sensor_data', limit=100000),
        'Gas': get_sensor_data(room_id, 'gas_sensor_data', limit=100000),
    }

    if not any(sensor_data.values()):
        st.warning("Keine Sensordaten verfügbar.")
        return

    df = pd.DataFrame()

    # Daten aus Tabellen holen
    temp_data = pd.DataFrame(sensor_data['Temperatur'], columns=['timestamp', 'temperature', 'humidity'])
    if not temp_data.empty:
        df['Temperatur'] = temp_data['temperature']
        df['Luftfeuchtigkeit'] = temp_data['humidity']

    lux_data = pd.DataFrame(sensor_data['Lichtintensität'], columns=['timestamp', 'lux'])
    if not lux_data.empty:
        df['Lichtintensität'] = lux_data['lux']

    gas_data = pd.DataFrame(sensor_data['Gas'], columns=['timestamp', 'ppm'])
    if not gas_data.empty:
        df['Gas'] = gas_data['ppm']

    # Zeitstempel in das richtige Format umwandeln
    df['timestamp'] = pd.to_datetime(temp_data['timestamp'])
    df.set_index('timestamp', inplace=True)

    # Heatmap-Daten vorbereiten, falls keine Daten vorhanden sind, wird eine Warnung ausgegeben
    if df.empty:
        st.warning("Keine Daten zum Erstellen einer Heatmap.")
        return

    # Interaktive Heatmap mit Plotly erstellen
    st.header("Interaktive Heatmap der Sensorwerte")

    fig = px.imshow(
        df.transpose(),  # Transponieren, um Sensoren auf der y-Achse anzuzeigen
        labels={'x': 'Zeit', 'y': 'Sensoren'},
        color_continuous_scale='Viridis',
        color_continuous_midpoint=500,  # Mittelwert für eine feinere Abstufung
        range_color=[0, 1000],  # Wertebereich für die Farbskala
        aspect='auto'  # Automatische Skalierung
    )

    # Farbskala für feinere Abstufungen (bis 1000)
    fig.update_layout(
        coloraxis_colorbar_tickvals=[0, 250, 500, 750, 1000],  # Tick-Werte definieren
        coloraxis_colorbar_ticktext=['0', '250', '500', '750', '1000']  # Tick-Beschriftungen
    )

    st.plotly_chart(fig)

def show_sensor_histogram(room_id):
    """
    Zeigt ein Histogramm zur Verteilung der Sensordaten für verschiedene Sensoren an, das die Häufigkeit der Werte über verschiedene Intervalle hinweg darstellt.
    
    :param room_id: Die ID des Raums, für den das Histogramm erstellt werden soll.
    """
    sensor_data = {
        'Temperatur': get_sensor_data(room_id, 'dht22_data', limit=100000),
        'Luftfeuchtigkeit': get_sensor_data(room_id, 'dht22_data', limit=100000),
        'Lichtintensität': get_sensor_data(room_id, 'light_sensor_data', limit=100000),
        'Gas': get_sensor_data(room_id, 'gas_sensor_data', limit=100000),
    }

    if not any(sensor_data.values()):
        st.warning("Keine Sensordaten verfügbar.")
        return

    df = pd.DataFrame()

    # Daten aus Tabellen holen
    temp_data = pd.DataFrame(sensor_data['Temperatur'], columns=['timestamp', 'temperature', 'humidity'])
    if not temp_data.empty:
        df['Temperatur'] = temp_data['temperature']
        df['Luftfeuchtigkeit'] = temp_data['humidity']

    lux_data = pd.DataFrame(sensor_data['Lichtintensität'], columns=['timestamp', 'lux'])
    if not lux_data.empty:
        df['Lichtintensität'] = lux_data['lux']

    gas_data = pd.DataFrame(sensor_data['Gas'], columns=['timestamp', 'ppm'])
    if not gas_data.empty:
        df['Gas'] = gas_data['ppm']

    if df.empty:
        st.warning("Keine Sensordaten zum Erstellen der Histogramme.")
        return

    # Erstelle die Histogramme für jeden Sensor
    st.header("🔂 Histogramme der Sensordaten")

    for sensor in df.columns:
        fig = px.histogram(
            df, 
            x=sensor, 
            nbins=30,  # Anzahl der Bins für die Aufteilung
            title=f"Verteilung der {sensor} Werte",
            labels={sensor: f"{sensor} Wert"},
            color_discrete_sequence=['#FF7F46']  # Farbwahl für das Histogramm
        )
        st.plotly_chart(fig)

def show_sensor_boxplots(room_id):
    """
    Zeigt Boxplots für die Verteilung der Sensordaten an, inklusive Quartilen, Median und Ausreißern,
    basierend auf der Auswahl des Benutzers (nur 1 Sensor).
    
    :param room_id: Die ID des Raums, für den die Boxplots erstellt werden sollen.
    """
    sensor_data = {
        'Temperatur': get_sensor_data(room_id, 'dht22_data', limit=1000),
        'Luftfeuchtigkeit': get_sensor_data(room_id, 'dht22_data', limit=1000),
        'Lichtintensität': get_sensor_data(room_id, 'light_sensor_data', limit=1000),
        'Gas': get_sensor_data(room_id, 'gas_sensor_data', limit=1000),
    }

    if not any(sensor_data.values()):
        st.warning("Keine Sensordaten verfügbar.")
        return

    # Daten aus Tabellen holen
    df = pd.DataFrame()

    temp_data = pd.DataFrame(sensor_data['Temperatur'], columns=['timestamp', 'temperature', 'humidity'])
    if not temp_data.empty:
        df['Temperatur'] = temp_data['temperature']
        df['Luftfeuchtigkeit'] = temp_data['humidity']

    lux_data = pd.DataFrame(sensor_data['Lichtintensität'], columns=['timestamp', 'lux'])
    if not lux_data.empty:
        df['Lichtintensität'] = lux_data['lux']

    gas_data = pd.DataFrame(sensor_data['Gas'], columns=['timestamp', 'ppm'])
    if not gas_data.empty:
        df['Gas'] = gas_data['ppm']

    if df.empty:
        st.warning("Keine Daten zum Erstellen eines Boxplots.")
        return

    # Interaktive Auswahl eines Sensors
    st.header("🔲 Wähle einen Sensor für die Boxplot-Darstellung")
    sensors = ['Temperatur', 'Luftfeuchtigkeit', 'Lichtintensität', 'Gas']
    selected_sensor = st.selectbox("Wähle einen Sensor", sensors)

    selected_data = df[[selected_sensor]]

    # Boxplot erstellen
    st.subheader(f"Boxplot der {selected_sensor} Werte")

    if not selected_data.empty:
        # Festlegen der richtigen Einheit basierend auf dem ausgewählten Sensor
        if selected_sensor == 'Temperatur':
            y_axis_label = 'Temperatur (°C)'
        elif selected_sensor == 'Luftfeuchtigkeit':
            y_axis_label = 'Luftfeuchtigkeit (%)'
        elif selected_sensor == 'Lichtintensität':
            y_axis_label = 'Lichtintensität (Lux)'
        else:  # Gas
            y_axis_label = 'Gas (ppm)'

        # Plotly Boxplot mit Ausreißern und zentrierter Darstellung
        fig = px.box(
            selected_data,
            labels={'value': y_axis_label, 'variable': 'Sensor'},
            points="outliers"  # Nur Ausreißer anzeigen, keine normalen Punkte
        )

        # Logarithmische Skalierung für die y-Achse (optional, um Ausreißer zu komprimieren)
        fig.update_layout(
            xaxis=dict(tickmode='array', tickvals=[0]),  # Zentrieren der Boxen auf der x-Achse
            yaxis_title=y_axis_label,
            yaxis=dict(
                type="log",  # Logarithmische Skalierung
                autorange=True
            )
        )

        # Boxplot anzeigen
        st.plotly_chart(fig)
    else:
        st.warning(f"Keine Daten für den Sensor {selected_sensor}.")

def show_sensor_scatterplot(room_id):
    sensor_data = {
        'Temperatur': get_sensor_data(room_id, 'dht22_data', limit=1000),
        'Luftfeuchtigkeit': get_sensor_data(room_id, 'dht22_data', limit=1000),
        'Lichtintensität': get_sensor_data(room_id, 'light_sensor_data', limit=1000),
        'Gas': get_sensor_data(room_id, 'gas_sensor_data', limit=1000),
    }

    if not any(sensor_data.values()):
        st.warning("Keine Sensordaten verfügbar.")
        return

    # Daten aus Tabellen holen
    df = pd.DataFrame()
    temp_data = pd.DataFrame(sensor_data['Temperatur'], columns=['timestamp', 'temperature', 'humidity'])
    if not temp_data.empty:
        df['Temperatur'] = temp_data['temperature']
        df['Luftfeuchtigkeit'] = temp_data['humidity']
        # Sicherstellen, dass der Zeitstempel als datetime interpretiert wird
        df['timestamp'] = pd.to_datetime(temp_data['timestamp'], errors='coerce')

    lux_data = pd.DataFrame(sensor_data['Lichtintensität'], columns=['timestamp', 'lux'])
    if not lux_data.empty:
        df['Lichtintensität'] = lux_data['lux']
        # Zeitstempel als datetime konvertieren
        df['timestamp'] = pd.to_datetime(lux_data['timestamp'], errors='coerce')

    gas_data = pd.DataFrame(sensor_data['Gas'], columns=['timestamp', 'ppm'])
    if not gas_data.empty:
        df['Gas'] = gas_data['ppm']
        # Zeitstempel als datetime konvertieren
        df['timestamp'] = pd.to_datetime(gas_data['timestamp'], errors='coerce')

    if df.empty:
        st.warning("Keine Daten für den Scatterplot.")
        return

    # Interaktive Auswahl eines Sensors mit Radiobuttons
    st.header("Wähle einen Sensor für den Scatterplot")
    sensors = ['Temperatur', 'Luftfeuchtigkeit', 'Lichtintensität', 'Gas']
    selected_sensor = st.radio("Wähle einen Sensor", sensors)

    selected_data = df[['timestamp', selected_sensor]]

    if not selected_data.empty:
        # Min- und Max-Werte des Sensors für die Farbskalierung
        min_value = selected_data[selected_sensor].min()
        max_value = selected_data[selected_sensor].max()

        # Festlegen der y-Achsen-Beschriftung
        if selected_sensor == 'Temperatur':
            y_axis_label = 'Temperatur (°C)'
        elif selected_sensor == 'Luftfeuchtigkeit':
            y_axis_label = 'Luftfeuchtigkeit (%)'
        elif selected_sensor == 'Lichtintensität':
            y_axis_label = 'Lichtintensität (Lux)'
        else:  # Gas
            y_axis_label = 'Gas (ppm)'

        # Scatterplot mit Plotly
        fig = px.scatter(
            selected_data,
            x='timestamp',  # Verwende den Zeitstempel als x-Achse
            y=selected_sensor,  # Sensorwerte als y-Achse
            color=selected_sensor,  # Farbskala basierend auf den Sensorwerten
            color_continuous_scale="Viridis",  # Farbskala, kann nach Wunsch geändert werden
            range_color=[min_value, max_value],  # Min- und Max-Werte definieren den Farbraum
            labels={selected_sensor: y_axis_label},
        )

        # Layout anpassen
        fig.update_layout(
            xaxis_title="Zeitpunkt",
            yaxis_title=y_axis_label,
            xaxis=dict(tickformat="%Y-%m-%d %H:%M:%S"),  # Zeitformat für x-Achse mit Datum und Zeit
        )

        # Scatterplot anzeigen
        st.plotly_chart(fig)
    else:
        st.warning(f"Keine Daten für den Sensor {selected_sensor}.")
def main():
    st.set_page_config(
        page_title="Sensors",
        page_icon="📊",
        layout="wide"
    )

    with open("pages/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title("📊 Sensor-Daten Visualisierung")
    selected_room_name = get_selected_room()

    if selected_room_name:
        room_id = db.get_room_id_by_name(selected_room_name)

        # Sensor-Metriken anzeigen
        show_sensor_metrics(room_id)

        # Sensor-Daten anzeigen
        get_even_spacing_for_sections()
        show_sensor_data_line_chart_limit(room_id)

        # Sensor-Daten nach Datum filtern
        get_even_spacing_for_sections()
        show_area_graph_with_filters(room_id)

        # Heatmap über Verlauf
        get_even_spacing_for_sections()
        show_sensor_heatmap(room_id)

        # Histogram um Anzahl Datenpunkte zu sehen
        get_even_spacing_for_sections()
        show_sensor_histogram(room_id)

        # Boxplot um Quartile, Median etc. auszugeben
        get_even_spacing_for_sections()
        show_sensor_boxplots(room_id)

        # Scatterplot für die Sensorwerte anzeigen
        get_even_spacing_for_sections()
        show_sensor_scatterplot(room_id)

if __name__ == "__main__":
    main()
