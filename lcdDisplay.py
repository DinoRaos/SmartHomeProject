import time
import board
import adafruit_dht
from RPLCD.i2c import CharLCD

# Initialize the DHT device and LCD
dhtDevice = adafruit_dht.DHT22(board.D4)
lcd = CharLCD('PCF8574', 0x27)

# Clear the display initially
lcd.clear()

while True:
    try:
        # Get temperature in Celsius and humidity
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity

        # Clear the display and write the values on the LCD
        lcd.clear()
        lcd.write_string("T: {:.1f}".format(temperature_c))  # First line
        lcd.write_string("\nH: {}%".format(humidity))              # Second line


    except RuntimeError as error:
        # Errors happen fairly often with DHT sensors, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    # Keep the values displayed for a while before the next update
    time.sleep(2.0)

