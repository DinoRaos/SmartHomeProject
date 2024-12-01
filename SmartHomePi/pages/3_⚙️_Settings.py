import streamlit as st
from database.db import Database

db = Database()

def main():
    st.title("⚙️ Raumverwaltung")
    
    # Raum hinzufügen / Prüfen
    st.header("Neuen Raum hinzufügen")
    room_name = st.text_input("Raumname", placeholder="z.B. Wohnzimmer")
    if st.button("Hinzufügen"):
        if room_name:
            if not db.get_room_id_by_name(room_name):
                db.insert_room(room_name)
                st.success(f"Raum '{room_name}' wurde hinzugefügt.")
            else:
                st.error("Raum existiert bereits.")
        else:
            st.error("Bitte geben Sie einen gültigen Namen ein.")

    # Alle Räume anzeigen lassen
    st.header("Vorhandene Räume")
    rooms = db.connection.execute("SELECT id, name FROM rooms").fetchall()
    for room_id, room_name in rooms:
        with st.container():
            st.subheader(room_name)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**ID:** {room_id}")
            with col2:
                if st.button("🗑️ Entfernen", key=f"delete_{room_id}"):
                    db.connection.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
                    db.connection.execute("DELETE FROM dht22_data WHERE room_id = ?", (room_id,))
                    db.connection.execute("DELETE FROM flame_sensor_data WHERE room_id = ?", (room_id,))
                    db.connection.execute("DELETE FROM gas_sensor_data WHERE room_id = ?", (room_id,))
                    db.connection.execute("DELETE FROM light_sensor_data WHERE room_id = ?", (room_id,))
                    db.connection.commit()
                    
                    st.rerun()
                    
if __name__ == "__main__":
    main()
