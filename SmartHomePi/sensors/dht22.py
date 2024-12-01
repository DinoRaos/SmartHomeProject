import time
import adafruit_dht
import board

class DHT22Sensor:
    def __init__(self, pin):
        """
        Initialisiert den DHT22-Sensor.
        :param pin: GPIO-Pin, an den der Sensor angeschlossen ist (als board.Pin-Objekt).
        """
        self.dht_device = adafruit_dht.DHT22(pin)
        self.is_active = True

    def read_data(self):
        """
        Liest Temperatur und Luftfeuchtigkeit aus.
        :return: Ein Dictionary mit Temperatur und Luftfeuchtigkeit oder None bei Fehlern.
        """
        try:
            temperature = self.dht_device.temperature
            humidity = self.dht_device.humidity
            if temperature is not None and humidity is not None:
                return {"temperature": round(temperature, 2), "humidity": round(humidity, 2)}
            else:
                return None
        except RuntimeError as e:
            print(f"Error reading sensor: {e}")
            return None

    def exit(self):
        """
        Stopt den Sensor und räumt auf, indem die Ressourcen freigegeben werden.
        """
        self.dht_device.exit()
        print("Sensor has been deactivated and cleaned up.")