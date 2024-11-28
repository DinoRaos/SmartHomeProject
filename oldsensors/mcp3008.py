import time
from gpiozero import MCP3008
from datetime import datetime

# MCP3008 Channels 0-7 (8 channel Version of MCP)
ldr = MCP3008(channel=0)  # LDR CH0
flame = MCP3008(channel=1)  # Flame Sensor CH1
mq2 = MCP3008(channel=2) # MQ-2 CH2

while True:
    # Values of Sensors 
    ldr_value = ldr.value  # Value 0-1
    mq2_value = mq2.value  # Value 0-1
    flame_value = flame.value  # Value 0-1
    
    # Timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    fire_detected = "Yes" if flame_value < 0.5 else "No"  # High base to low for now ~0,5 around 8cm away

    # Format for now printing to console
    print(f"Timestamp: {timestamp}")
    print(f"Sensor: LDR")
    print(f"Rohwert: {ldr_value:.2f}")
    print("-" * 40)

    print(f"Timestamp: {timestamp}")
    print(f"Sensor: MQ-2")
    print(f"Rohwert: {mq2_value:.2f}")
    print("-" * 40)

    print(f"Timestamp: {timestamp}")
    print(f"Sensor: Flame")
    print(f"Rohwert: {flame_value:.2f}")
    print(f"Feuer erkannt: {fire_detected}")
    print("-" * 40)

    time.sleep(2)
