# main.py
# HDC302x environmental monitor
# MicroPython / Raspberry Pi Pico W
#
# Copyright (c) 2026 Sophia J Anderson
#
# Main application loop for SD logging, BLE file transfer,
# and environmental sensor recording.
#
# Project modules by Sophia J Anderson:
# - sensors.py
# - SD_Card.py
# - log_manager.py
# - ble_manager.py

# === Imports ===
import time
from machine import Pin, I2C, SPI
import sensors
import SD_Card
from SD_Card import spi, cs
import log_manager
from log_manager import log_environmental_data
from ble_manager import BLEManager

# === Initialize SD system ===
SD_Card.init()

# === BLE file access commands ===
file_passwords = {
    "TEMP": "/sd/temperature_log.csv",
    "HUMD": "/sd/humidity_log.csv",

}

ble_mgr = BLEManager(spi, cs, file_passwords)

# === SD Card Mount (Yes/No) & Prints ===
print("SD mounted:", SD_Card.sd_mounted)
print()
print("=============== ENVIRONMENTAL MONITOR ==============")
print()

# === Timing configuration ===
LOG_INTERVAL_MS = 120_000
last_log_time = time.ticks_ms()

# === Main Loop ===
while True:
    SD_Card.update()

    if ble_mgr:
        try:
            ble_mgr.update()

            if ble_mgr.send_file_flag and ble_mgr.file_handle:
                SD_Card.sd_busy = False

        except Exception as e:
            print("[BLE_UPDATE ERROR]", e)

    now = time.ticks_ms()

    if not ble_mgr.send_file_flag:
        # only log when BLE is not transferring
        if time.ticks_diff(now, last_log_time) >= LOG_INTERVAL_MS:
            timestamp, temperatures0, humidities0, get_temperature_celcius1, get_humidity1 = sensors.prints()
            log_environmental_data(temperatures0, humidities0)
            last_log_time = now

    time.sleep_ms(50)
