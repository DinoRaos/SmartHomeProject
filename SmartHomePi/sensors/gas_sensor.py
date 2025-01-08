from sensors.mcp3008 import MCP3008Sensor

class GasSensor:
    from sensors.mcp3008 import MCP3008Sensor

class GasSensor:
    def __init__(self, channel):
        from gpiozero import MCP3008
        self.sensor = MCP3008(channel=channel)

    def read_raw_value(self):
        """Lese den Rohwert (zwischen 0 und 1) vom Sensor."""
        return self.sensor.value

    def read_gas_level(self):
        """Konvertiere den Rohwert in ppm."""
        raw_value = self.read_raw_value()

        #Rohwert in ppm umrechnen (keine Kali)
        max_ppm = 1000
        ppm = raw_value * max_ppm
        return round(ppm, 2)


