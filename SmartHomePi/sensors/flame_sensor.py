from sensors.mcp3008 import MCP3008Sensor

class FlameSensor:
    def __init__(self, channel):
        from gpiozero import MCP3008
        self.sensor = MCP3008(channel=channel)

    def read_raw_value(self):
        """Lese den Rohwert (zwischen 0 und 1) vom Sensor."""
        return self.sensor.value

    def is_fire_detected(self, threshold=0.5):
        """
        Ermittelt, ob ein Feuer erkannt wurde.
        :param threshold: Schwelle für Feuererkennung (niedriger Wert = Feuer).
        """
        raw_value = self.read_raw_value()
        return raw_value < threshold
