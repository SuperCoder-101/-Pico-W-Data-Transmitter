# Pico-W-Data-Transmitter
A low-level MicroPython BLE UART peripheral manager inspired by the official [ble_simple_peripheral.py](https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_simple_peripheral.py) example, with aioble-style organization, plus SD-card-backed command/file transfer logic.

>[!Note]
>This library was created using MicroPython V1.28.0

# Features
- I've tested this using Android, not sure if it works on Iphone
- 
# About this repository
This repository contains the following:
- lib/
- doc/
- examples/


# Bluetooth Data Collection - SOP
Before starting, ensure the **Bluetooth library is installed on the Pico Pi W** and that your main script includes the required Bluetooth initialization lines.

## Step 1:
Download **Serial Bluetooth Terminal** from the App Store.

<img width="425" height="401" alt="image" src="https://github.com/user-attachments/assets/04ed6f6e-0f91-4072-821e-550ec6e3f1ca" />

## Step 2:
Open **Serial Bluetooth Terminal.**

## Step 3:
Tap the **three-line menu** in the upper-left corner.

<img width="442" height="384" alt="image" src="https://github.com/user-attachments/assets/8e7ead4a-1c5c-49ad-b3a8-2294bd71182e" />

## Step 4:
Select the **Devices** tab.

<img width="452" height="484" alt="image" src="https://github.com/user-attachments/assets/8d20c013-5542-4a80-b82e-4352ec7d7c20" />

## Step 5:
Choose **Bluetooth LE**, then press **Scan**.
- Your Pico device should appear after the scan completes.

<img width="464" height="498" alt="image" src="https://github.com/user-attachments/assets/e58b0393-9321-4c08-b72e-e4b0ad63a416" />

## Step 6:
Return to the **Terminal** screen and choose one of the **macro buttons** above the input line.
- **Hold down** on the macro to edit it.

<img width="448" height="478" alt="image" src="https://github.com/user-attachments/assets/66e88aeb-d087-4e73-999c-f53f112f54a5" />

## Step 7:
Rename the macro based on the data you are collecting.
Update the macro **value** to match the password you assigned for that data type.
- The password can be edited inside the Bluetooth script.

<img width="429" height="488" alt="image" src="https://github.com/user-attachments/assets/c45dc63a-27e2-4514-9f9d-91a4698c3fce" />

## Step 8:
Go back to the Terminal and **tap** your newly labeled macro once (do not hold). 
- Data will only appear after it has been written to the Pico's log file.
- If the log file has no data yet, the macro command will not return anything.

## Step 9:
Once you have collected your data, tap the **three horizontal dots** in the upper-right corner of the Terminal page.

You have two options:
- **Data Tab**:
  - Tap **Save** to store the file in your phone's default location.
  - Tap **Export** to choose a specific folder or app to save your data.

- **Configuration Tab**:
  - Allows you to adjust app settings if needed.

Make sure to look from **left to right** when referring to the photos below (**do not** look at the top left picture first, then the bottom left, it should be **top left -> top right -> bottom left -> bottom right** in that order)

<img width="464" height="447" alt="image" src="https://github.com/user-attachments/assets/e5ead50b-f0c2-4066-aad4-74225bacbaca" />
<img width="490" height="447" alt="image" src="https://github.com/user-attachments/assets/74c9be24-ebe8-4822-9dbd-77a5af46706f" />
<img width="472" height="461" alt="image" src="https://github.com/user-attachments/assets/2ad5a6b7-efa1-4b7c-842e-5548b4bec755" />
<img width="478" height="461" alt="image" src="https://github.com/user-attachments/assets/222c8a78-1629-40d8-9275-c63d4f64ad9f" />

**Code needed**:
- ble_manager.py
**Then place this code at the beginning of the main.py file (aka after all the imports)

### Example Code:
```python
from ble_manager import BLEManager 
 
# SPI setup (matches your existing wiring) 
spi = SPI(1, 
    baudrate=1_000_000, 
    polarity=0, 
    phase=0, 
    bits=8, 
    firstbit=SPI.MSB, 
    sck=Pin(10), 
    mosi=Pin(11), 
    miso=Pin(8)) 
 
cs = Pin(9, Pin.OUT) 
 
file_passwords = { 
    "INA219": "/sd/ina219_log.csv", 
    "ENV": "/sd/environment_log.csv", 
    "VIB": "/sd/vibration_log.csv", 
    "XYZ": "/sd/xyz_log.csv", 
    "HEART": "/sd/heartbeat.txt", 
    "MEM": "/sd/mem_log.txt", 
} 
 
ble_mgr = BLEManager(spi, cs, file_passwords) 
```
>[!Note]
>The below is for a project I did for the USDA Sensor Group, so please ignore the below unless you are looking at this repository regarding the Bumble Bee Transport Project.

**Then place this in the main loop before the comment "check for restart request". Make sure it is lined up with the code below that comment.**

```python
        # Update BLE Manager 
        if ble_mgr: 
            try: 
                ble_mgr.update()  # This handles file transfers 
            except Exception as e: 
                log_sensor_error("BLE_UPDATE", e, context="main_loop")         
```



