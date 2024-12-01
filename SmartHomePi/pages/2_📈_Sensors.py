import streamlit as st
from database.db import Database
import pandas as pd

db = Database()

def main():
    st.title("📊 Sensor-Daten")

    rooms = db.connection.execute("SELECT id, name FROM rooms").fetchall()
    if not rooms:
        st.warning("Es gibt keine verfügbaren Räume. Bitte erstellen Sie zuerst einen Raum unter ⚙️ Einstellungen.")
        return

    room_names = [room_name for _, room_name in rooms]
    selected_room = st.selectbox("Raum auswählen", room_names)

    if selected_room:
        room_id = db.get_room_id_by_name(selected_room)
        st.subheader(f"Sensor-Daten für {selected_room}")

        # Aktuellste Daten holen
        dht_data = db.connection.execute(f"SELECT * FROM dht22_data WHERE room_id = ? ORDER BY timestamp DESC LIMIT 1", (room_id,)).fetchone()
        light_data = db.connection.execute(f"SELECT * FROM light_sensor_data WHERE room_id = ? ORDER BY timestamp DESC LIMIT 1", (room_id,)).fetchone()
        flame_data = db.connection.execute(f"SELECT * FROM flame_sensor_data WHERE room_id = ? ORDER BY timestamp DESC LIMIT 1", (room_id,)).fetchone()
        gas_data = db.connection.execute(f"SELECT * FROM gas_sensor_data WHERE room_id = ? ORDER BY timestamp DESC LIMIT 1", (room_id,)).fetchone()

        # TODO: In Graphen
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🌡️ Temperatur", f"{dht_data[3]}°C" if dht_data else "Keine Daten")
            st.metric("🔥 Feuer", "Ja" if flame_data and flame_data[3] else "Nein")
        with col2:
            st.metric("💧 Luftfeuchtigkeit", f"{dht_data[4]}%" if dht_data else "Keine Daten")
            st.metric("💨 Gas (PPM)", f"{gas_data[3]}" if gas_data else "Keine Daten")
        
        st.metric("💡 Lichtintensität (LUX)", f"{light_data[3]}" if light_data else "Keine Daten")

if __name__ == "__main__":
    main()
