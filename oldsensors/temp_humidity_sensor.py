import time
import board
import adafruit_dht

# Initialize the DHT device, with data pin connected to: (Here gpio 4)
dhtDevice = adafruit_dht.DHT22(board.D4)

while True:
    try:
        # Get temperature in Celsius and humidity
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity

        # Print the values in Celsius and humidity only
        print("Temp: {:.1f} C    Humidity: {}%".format(temperature_c, humidity))

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2.0)

