import time
import board
import threading
import streamlit as st
from sensors.dht22 import DHT22Sensor
from sensors.flame_sensor import FlameSensor
from sensors.gas_sensor import GasSensor
from sensors.light_sensor import LightSensor
from database.db import Database
from sensors.lcd_display import LCDDisplay

# Globale Event-Variable für den Stop-Mechanismus
stop_thread_event = threading.Event()

def run_sensors(selected_room, stop_event):
    db = Database()

    # ID des ausgewählten Raums holen
    room_id = db.get_room_id_by_name(selected_room)

    # Sensoren initialisieren
    dht22 = DHT22Sensor(pin=board.D4)
    light_sensor = LightSensor(channel=0)
    flame_sensor = FlameSensor(channel=1)
    gas_sensor = GasSensor(channel=2)

    # LCD Display initialisieren
    lcd = LCDDisplay(selected_room, {"temperature": 0.0, "humidity": 0.0}, 0.0, 0.0)

    # Starte die Anzeige im Hintergrund 
    lcd_process = threading.Thread(target=lcd.run)
    lcd_process.start()

    while not stop_event.is_set():  # Überprüfe regelmäßig, ob das Event gesetzt wurde
        try:
            # DHT22 (Temperatur/Feuchtigkeit)
            dht_data = dht22.read_data()
            if dht_data:
                db.insert_data("dht22_data", room_id, dht_data["temperature"], dht_data["humidity"])

                # Update die LCD-Anzeige mit den neuesten Werten
                lcd.dht_data = dht_data

            # Flame-Sensor (Feuer erkannt?)
            fire_detected = flame_sensor.is_fire_detected()
            fs_raw = flame_sensor.read_raw_value()
            db.insert_data("flame_sensor_data", room_id, fire_detected, fs_raw)

            # MQ-2 Gas-Sensor (PPM)
            gas_level = gas_sensor.read_gas_level()
            gas_raw = gas_sensor.read_raw_value()
            db.insert_data("gas_sensor_data", room_id, gas_level, gas_raw)

            # KYR-08 Licht-Sensor (LUX)
            light_level = light_sensor.read_light_level()
            light_raw = light_sensor.read_raw_value()
            db.insert_data("light_sensor_data", room_id, light_level, light_raw)

            # Update die LCD-Anzeige mit den neuesten Licht- und Gaswerten
            lcd.light_level = light_level
            lcd.gas_level = gas_level

        except Exception as e:
            print(f"Fehler beim Auslesen eines Sensors: {str(e)}")

        time.sleep(10)

    # WICHTIG: DHT22 muss immer mit exit geschlossen werden sonst pin 4 error + LCD cleanup
    print("Sensorprozess gestoppt.")
    lcd.stop()
    dht22.exit()
    lcd_process.join()
