import board
import adafruit_dht

class DHT22Sensor:
    def __init__(self, pin):
        """
        Initialisiert den DHT22-Sensor.
        :param pin: GPIO-Pin, an den der Sensor angeschlossen ist (als board.Pin-Objekt).
        """
        self.dht_device = adafruit_dht.DHT22(pin)

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
        except RuntimeError as e:
            return None
