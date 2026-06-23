# Pico-W Data Transmitter

## Overview

The Pico-W Data Transmitter is a MicroPython-based Bluetooth Low Energy (BLE) data transfer framework developed for the Raspberry Pi Pico W.

This project is based on MicroPython's [`ble_simple_peripheral.py`](https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_simple_peripheral.py) example, reorganized with an aioble-style structure and expanded with SD-card-backed command and file transfer logic.

The repository provides BLE UART communication, password-protected file retrieval, SD card data access, log management utilities, and sensor integration support for embedded data collection projects.

---

## Features

* BLE UART communication
* SD-card-backed file transfer
* Password-protected file retrieval
* Log file management
* Sensor data collection support
* Raspberry Pi Pico W compatibility
* MicroPython-based implementation
* Lightweight embedded design

---

## Repository Structure

```text
Pico-W-Data-Transmitter/
├── README.md
├── LICENSE
├── main.py
├── ble_manager.py
├── log_manager.py
├── SD_Card.py
├── sensors.py
├── docs/
│   ├── Ble_Manager_Info.docx
│   └── Bluetooth_SOP.docx
└── lib/
    └── sdcard.py
```

---

## File Descriptions

| File             | Description                                                        |
| ---------------- | ------------------------------------------------------------------ |
| `main.py`        | Example application entry point                                    |
| `ble_manager.py` | BLE UART peripheral manager with command and file transfer support |
| `log_manager.py` | Log file creation and management utilities                         |
| `SD_Card.py`     | SD card mounting, writing, and file access support                 |
| `sensors.py`     | Sensor integration and data collection support                     |
| `lib/sdcard.py`  | MicroPython SD card driver                                         |

---

## Requirements

* Raspberry Pi Pico W
* MicroPython
* Bluetooth-capable phone, tablet, or computer
* MicroSD card module
* Optional connected sensors

---

## Bluetooth Workflow

1. The Pico W advertises as a BLE peripheral.
2. A client device connects over BLE UART.
3. The client sends a command or password.
4. The Pico W checks the command against available log files.
5. Matching files are read from the SD card.
6. Data is sent wirelessly over BLE notifications.

---

## Documentation

Additional documentation is available in the `docs/` folder:

* `Ble_Manager_Info.docx`
* `Bluetooth_SOP.docx`

---

## License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.

---

## Author

Sophia J. Anderson
