'''
Copyright (c) 2026 Sophia J Anderson

This project contains code inspired by and partially adapted from
MicroPython BLE examples:

https://github.com/micropython/micropython/tree/master/examples/bluetooth

MicroPython Copyright (c) 2013-2026 Damien P. George
Licensed under the MIT License.
'''

from machine import Pin, SPI
import os, sdcard, ubluetooth, struct, time
import log_manager
import SD_Card

class BLEManager:
    # Class constants to save memory
    UART_SERVICE_UUID = ubluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
    UART_TX_UUID = ubluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
    UART_RX_UUID = ubluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
    
    # BLE event constants
    _IRQ_CENTRAL_CONNECT = 1
    _IRQ_CENTRAL_DISCONNECT = 2
    _IRQ_GATTS_WRITE = 3
    
    def __init__(self, spi, cs, file_map, ble_name="PicoW-BLE-File", chunk_size=20):
        self.ble = ubluetooth.BLE()
        self.ble.active(True)

        self.spi = spi
        self.cs = cs
        self.sd = None
        self.vfs = None

        self.FILE_PASSWORDS = file_map
        self.conn_handle = None
        self.tx_handle = None
        self.rx_handle = None
        self.current_file = None
        self.send_file_flag = False
        self.ble_name = ble_name
        self.chunk_size = chunk_size  # For efficient data transmission
        
        # File transfer state
        self.file_handle = None
        self.transfer_position = 0

        self._init_ble_services()
        self.advertise()

    def mount_sd(self):
        """Mount SD card with better error handling."""
        if self.sd is not None:  # Already mounted
            return True
            
        try:
            self.sd = sdcard.SDCard(self.spi, self.cs)
            self.vfs = os.VfsFat(self.sd)
            os.mount(self.vfs, "/sd")
            print("[BLE] SD card mounted at /sd")
            return True
        except OSError as e:
            print(f"[BLE] SD mount failed: {e}")
            return False

    def _init_ble_services(self):
        """Initialize BLE services with optimized settings."""
        UART_TX = (self.UART_TX_UUID, ubluetooth.FLAG_NOTIFY)
        UART_RX = (self.UART_RX_UUID, ubluetooth.FLAG_WRITE)
        UART_SERVICE = (self.UART_SERVICE_UUID, (UART_TX, UART_RX))
        
        ((self.tx_handle, self.rx_handle),) = self.ble.gatts_register_services((UART_SERVICE,))
        self.ble.irq(self._bt_irq)

    def advertise(self):
        """Start BLE advertising with power-efficient settings."""
        name_bytes = self.ble_name.encode('utf-8')
        # Limit name length to save power
        if len(name_bytes) > 29:
            name_bytes = name_bytes[:29]
            
        payload = struct.pack("BB", len(name_bytes) + 1, 0x09) + name_bytes
        # Increase interval to 500ms for better power efficiency
        self.ble.gap_advertise(500, adv_data=payload)
        print(f"[BLE] Advertising as '{self.ble_name}' (power-efficient)")

    def _bt_irq(self, event, data):
        """Handle BLE events efficiently."""
        if event == self._IRQ_CENTRAL_CONNECT:
            self.conn_handle = data[0]
            print("[BLE] Device connected")
            # Stop advertising to save power when connected
            self.ble.gap_advertise(None)

        elif event == self._IRQ_CENTRAL_DISCONNECT:
            print("[BLE] Device disconnected")
            self.conn_handle = None
            self._cleanup_transfer()
            # Resume advertising
            self.advertise()

        elif event == self._IRQ_GATTS_WRITE:
            self._handle_command()

    def _handle_command(self):
        """Handle incoming BLE commands with better error handling."""
        try:
            cmd_bytes = self.ble.gatts_read(self.rx_handle)
            if not cmd_bytes:
                return
                
            cmd = cmd_bytes.decode('utf-8').strip().upper()
            print(f"[BLE] Command received: {cmd}")
            
            if cmd in self.FILE_PASSWORDS:
                self.current_file = self.FILE_PASSWORDS[cmd]
                print(f"[BLE] Authorized to send: {self.current_file}")
                self.send_file_flag = True
                self.transfer_position = 0
            elif cmd == "STOP":
                self._cleanup_transfer()
                self.send_line("TRANSFER_STOPPED")
            else:
                print("[BLE] Invalid command received")
                self.send_line("INVALID_COMMAND")
                
        except (UnicodeDecodeError, OSError) as e:
            print(f"[BLE] Command decode error: {e}")

    def _cleanup_transfer(self):
        """Clean up file transfer state."""
        if self.file_handle:
            try:
                self.file_handle.close()
            except:
                pass
            self.file_handle = None
        self.send_file_flag = False
        self.current_file = None
        self.transfer_position = 0

    def send_line(self, line):
        """Send data via BLE with size limits."""
        if not self.conn_handle:
            return False
            
        try:
            # Convert to bytes if string
            if isinstance(line, str):
                data = line.encode('utf-8')
            else:
                data = line
                
            # Split into chunks if too large for BLE MTU
            max_chunk = min(self.chunk_size, 20)  # BLE default MTU is ~23 bytes
            
            for i in range(0, len(data), max_chunk):
                chunk = data[i:i + max_chunk]
                self.ble.gatts_notify(self.conn_handle, self.tx_handle, chunk)
                if len(data) > max_chunk:
                    time.sleep_ms(10)  # Small delay for large transfers
            return True
            
        except OSError as e:
            print(f"[BLE] Notify error: {e}")
            return False
    
    def log(self, message):
        """Send log message via BLE with fallback to print."""
        print(f"[BLE LOG] {message}")
        if self.conn_handle:
            self.send_line(f"LOG: {message}\n")

    def update(self):
        """Non-blocking file transfer with power efficiency."""
        # Skip if SD is busy or no transfer requested
        if SD_Card.sd_busy or not self.send_file_flag or not self.current_file:
            return

        try:
            # Open file if not already open
            if not self.file_handle:
                SD_Card.sd_busy = True
                self.file_handle = open(self.current_file, "r")
                self.send_line("TRANSFER_START")
                print(f"[BLE] Starting transfer of {self.current_file}")

            # Read and send one line per update call (non-blocking)
            line = self.file_handle.readline()
            if line:
                line = line.strip()
                if line:  # Skip empty lines
                    success = self.send_line(f"{self.transfer_position}:{line}")
                    if success:
                        self.transfer_position += 1
                        print(f"[BLE] Sent line {self.transfer_position}: {line}")
                    else:
                        # Connection lost, cleanup
                        self._cleanup_transfer()
                        SD_Card.sd_busy = False
            else:
                # File complete
                self.send_line("TRANSFER_COMPLETE")
                print("[BLE] Transfer complete")
                self._cleanup_transfer()
                SD_Card.sd_busy = False

        except OSError as e:
            print(f"[BLE] File transfer error: {e}")
            self.send_line(f"TRANSFER_ERROR: {e}")
            self._cleanup_transfer()
            SD_Card.sd_busy = False

    def deinit(self):
        """Properly cleanup BLE resources."""
        self._cleanup_transfer()
        if SD_Card.sd_busy:
            SD_Card.sd_busy = False
        self.ble.gap_advertise(None)
        self.ble.active(False)
        print("[BLE] BLE manager deinitialized")
