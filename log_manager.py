# log_manager.py
# Excel-friendly environmental logger
# MicroPython / Raspberry Pi Pico W
#
# Copyright (c) 2026 Sophia J Anderson
#
# Records environmental sensor data to CSV files stored
# on the SD card. Log files are formatted for easy import
# into spreadsheet applications such as Microsoft Excel,
# LibreOffice Calc, and Google Sheets.
#
# This file is part of Sophia J Anderson's & Nolan Hoffs environmental monitoring project.

import time

from SD_Card import write_log_line

# Temperature log file
TEMP_LOG_FILE = "/sd/temperature_log.csv"

# Humidity log file
HUMIDITY_LOG_FILE = "/sd/humidity_log.csv"

# CSV headers
TEMP_HEADER = "Time,""Sensor 1,""Sensor 2,""Sensor 3"

HUMIDITY_HEADER = "Time,""Sensor 1,""Sensor 2,""Sensor 3"


# Log full environmental dataset
def log_environmental_data(temperatures,humidities):

    try:

        # Real date/time timestamp
        now = time.localtime()

        timestamp = "{:04d}-{:02d}-{:02d} ""{:02d}:{:02d}:{:02d}".format(now[0],now[1],now[2],now[3],now[4],now[5])

        # =========================
        # Temperature CSV Row
        # =========================

        temp_line = "{},""{:.2f}°C,""{:.2f}°C,""{:.2f}°C".format(timestamp,temperatures[0],temperatures[1],temperatures[2])

        # =========================
        # Humidity CSV Row
        # =========================

        humidity_line = "{},""{:.2f}%,""{:.2f}%,""{:.2f}%".format(timestamp,humidities[0],humidities[1],humidities[2])

        # =========================
        # Write Temperature Log
        # =========================

        temp_success = write_log_line(TEMP_LOG_FILE, temp_line, header=TEMP_HEADER)

        if not temp_success:

            print("[TEMP LOG ERROR]")

        # =========================
        # Write Humidity Log
        # =========================

        humidity_success = write_log_line(HUMIDITY_LOG_FILE, humidity_line, header=HUMIDITY_HEADER)

        if not humidity_success:

            print("[HUMIDITY LOG ERROR]")

        return (temp_success and humidity_success)

    except Exception as e:

        print("[ENV LOG ERROR]", e)

        return False
