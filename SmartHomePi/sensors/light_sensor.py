from sensors.mcp3008 import MCP3008Sensor

class LightSensor:
    from sensors.mcp3008 import MCP3008Sensor

class LightSensor:
    def __init__(self, channel):
        from gpiozero import MCP3008
        self.sensor = MCP3008(channel=channel)

    def read_raw_value(self):
        """Lese den Rohwert (zwischen 0 und 1) vom Sensor."""
        return self.sensor.value

    def read_light_level(self):
        """Konvertiere den Rohwert in Lux."""
        raw_value = self.read_raw_value()

        # Inverse Skalierung: 1 (dunkel) → 0 Lux, 0 → 1000 Lux (Beispiel) (keine Kali)
        max_lux = 1000
        lux = (1 - raw_value) * max_lux  # Dunkel: 0 Lux, Hell: max_lux
        return round(lux, 2)

