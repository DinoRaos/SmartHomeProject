import time
import threading
from RPLCD.i2c import CharLCD

class LCDDisplay:
    """
    Diese Klasse übernimmt die Steuerung des LCD-Displays.
    Sie zeigt die Daten der verschiedenen Sensoren auf dem LCD an.
    """

    def __init__(self, room_name, dht_data, light_level, gas_level):
        """
        Initialisiert das LCD und zeigt den Raumnamen und Sensorwerte an.
        
        :param room_name: Der Name des Raumes.
        :param dht_data: Die Daten vom DHT22 Sensor (Temperatur und Feuchtigkeit).
        :param light_level: Der Lichtwert vom Lichtsensor (LUX).
        :param gas_level: Der Gaswert vom Gassensor (PPM).
        """
        self.lcd = CharLCD('PCF8574', 0x27)  # LCD über I2C
        self.room_name = room_name
        self.dht_data = dht_data
        self.light_level = light_level
        self.gas_level = gas_level
        self._stop_event = threading.Event()

    def display(self):
        try:
            self.lcd.clear()
    
            room_display = "Raum: {}".format(self.room_name)
    
            if len(room_display) > 16:
                self.lcd.write_string(room_display[:16])
                self.lcd.cursor_pos = (1, 0)
                self.lcd.write_string(room_display[16:])
            else:
                self.lcd.write_string(room_display)
    
            time.sleep(3)
    
            self.lcd.clear()
            self.lcd.write_string("Temp: {:.1f}C".format(self.dht_data["temperature"]))
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string("Humid: {}%".format(self.dht_data["humidity"]))
            time.sleep(3)
    
            self.lcd.clear()
            self.lcd.write_string("Licht: {:.1f} LUX".format(self.light_level))
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string("Gas: {:.1f} PPM".format(self.gas_level))
            time.sleep(3)
    
        except Exception as e:
            print(f"Fehler beim Anzeigen auf dem LCD: {e}")


    def run(self):
        """
        Führt die Anzeige der Werte in regelmäßigen Abständen aus.
        Der Prozess kann über das _stop_event gestoppt werden.
        """
        while not self._stop_event.is_set():
            self.display()
            time.sleep(3)
        print("LCD Display wurde gestoppt.")

    def stop(self):
        """
        Stoppt das kontinuierliche Ausführen der Anzeige.
        """
        self._stop_event.set()

