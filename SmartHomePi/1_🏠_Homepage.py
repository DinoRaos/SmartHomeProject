import streamlit as st
import threading
from main import run_sensors, stop_thread_event  # Importiere das Stop-Event
from database.db import Database

db = Database()

# Flag zum Stoppen des Hintergrundthreads
def stop_sensors():
    st.session_state['sensor_running'] = False
    stop_thread_event.set()  # Setze das Stop-Event, um den Thread zu stoppen

# Funktion für das Haupt-Dashboard
def main():
    st.title("🏠 Smart Home Dashboard")
    
    st.write("Willkommen! Hier können Sie die Sensoren für einen Raum starten und die aktuellen Werte sehen.")
    
    # Räume anzeigen und auswählen
    rooms = db.connection.execute("SELECT id, name FROM rooms").fetchall()
    if rooms:
        room_names = [room_name for _, room_name in rooms]
        selected_room = st.selectbox("Raum auswählen", room_names)

        # Speichern des aktuellen Status der Sensoren
        if 'sensor_running' not in st.session_state:
            st.session_state['sensor_running'] = False

        # Button für Start/Stop basierend auf dem aktuellen Zustand der Sensoren
        button_text = "🚀 Sensoren starten" if not st.session_state['sensor_running'] else "🛑 Sensoren stoppen"
        
        if st.button(button_text):
            if st.session_state['sensor_running']:
                stop_sensors()
                st.rerun()
            else:
                st.session_state['sensor_running'] = True
                stop_thread_event.clear()
                threading.Thread(target=run_sensors, args=(selected_room, stop_thread_event), daemon=True).start()
                st.rerun()

    else:
        st.warning("Es gibt keine verfügbaren Räume. Bitte erstellen Sie zuerst einen Raum unter ⚙️ Einstellungen.")

if __name__ == "__main__":
    main()
