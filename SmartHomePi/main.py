import time
import board
from sensors.dht22 import DHT22Sensor
from sensors.flame_sensor import FlameSensor
from sensors.gas_sensor import GasSensor
from sensors.light_sensor import LightSensor
from database.db import Database
from sensors.lcd_display import LCDDisplay  # Import der LCDDisplay-Klasse

def main():
    db = Database()

    # Raum erstellen (wenn noch nicht vorhanden)
    room_name = "Schlafzimmer"
    room_id = db.get_room_id_by_name(room_name)

    if room_id is None:
        db.insert_room(room_name)
        room_id = db.get_room_id_by_name(room_name)

    # Sensoren initialisieren
    dht22 = DHT22Sensor(pin=board.D4)  # DHT22 Sensor an GPIO4
    light_sensor = LightSensor(channel=0)  # KYR-08 an Kanal 0 von MCP
    flame_sensor = FlameSensor(channel=1)  # Flame-Sensor an Kanal 1 von MCP
    gas_sensor = GasSensor(channel=2)  # MQ-2 Gas-Sensor an Kanal 2 von MCP

    # LCD Display initialisieren
    lcd = LCDDisplay(room_name, {"temperature": 0.0, "humidity": 0.0}, 0.0, 0.0)

    # Starte die Anzeige im Hintergrund
    lcd_process = threading.Thread(target=lcd.run)
    lcd_process.start()

    while True:
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
            # Fehlerbehandlung und Loggen des Fehlers
            print(f"Fehler beim Auslesen eines Sensors: {str(e)}")

        # Schlafzeit (zwischen den Sensorablesungen)
        time.sleep(60)

if __name__ == "__main__":
    import threading
    main()
