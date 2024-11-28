import time
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

    def display(self):
        """
        Zeigt den Raum, die Temperatur, Feuchtigkeit, Licht- und Gaswerte auf dem LCD an.
        """
        self.lcd.clear()

        room_display = "Raum: {}".format(self.room_name)

        # Wenn der gesamte Text (inkl. "Raum: ") länger als 16 Zeichen ist, teilen wir den Text auf
        if len(room_display) > 16:
            self.lcd.write_string(room_display[:16])
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string(room_display[16:])
        else:
            self.lcd.write_string(room_display)

        time.sleep(3)

        # Zeige die Temperatur und Feuchtigkeit an
        self.lcd.clear()
        self.lcd.write_string("Temp: {:.1f}C".format(self.dht_data["temperature"]))
        self.lcd.cursor_pos = (1, 0)  # Setze den Cursor in die zweite Zeile
        self.lcd.write_string("Humid: {}%".format(self.dht_data["humidity"]))
        time.sleep(3)

        # Zeige den Lichtwert und Gaswert an
        self.lcd.clear()
        self.lcd.write_string("Licht: {:.1f} LUX".format(self.light_level))
        self.lcd.cursor_pos = (1, 0)  # Setze den Cursor wieder auf die zweite Zeile
        self.lcd.write_string("Gas: {:.1f} PPM".format(self.gas_level))
        time.sleep(3)

    def run(self):
        """
        Führt die Anzeige der Werte in regelmäßigen Abständen aus.
        """
        while True:
            self.display()
            time.sleep(3)
