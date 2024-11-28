from gpiozero import MCP3008

class MCP3008Sensor:
    """
    Diese Klasse verwaltet den MCP3008 Analog-Digital-Wandler (ADC) zur Erfassung analoger Sensorwerte
    über den SPI-Bus des Raspberry Pi.
    """

    def __init__(self, channel):
        """
        Initialisiert den MCP3008-Sensor und legt den Kanal fest, auf dem der Sensor angeschlossen ist.
        
        :param channel: Der Kanal des MCP3008, der den Sensorwert liest (0 bis 7).
        """
        self.sensor = MCP3008(channel=channel)

    def read_value(self):
        """
        Liest den aktuellen Wert vom Sensor. Der Wert wird als Fließkommazahl zwischen 0 und 1 zurückgegeben,
        wobei 0 den minimalen Wert (0V) und 1 den maximalen Wert (entspricht 5V) darstellt.

        :return: Der Wert des Sensors als Fließkommazahl zwischen 0 und 1.
        """
        return self.sensor.value

