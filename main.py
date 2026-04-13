#STANDARD VERSION - Simple LED Output of a single color on a single APA102 LED string
from micropython import alloc_emergency_exception_buf
from lcd1602 import LCD1602
import gc
import dmx512_rx
import config
import uasyncio
import utime

# mock class should the LCD not be detected
class NoLcd:
    def print_lcd(self, _m):
        return
    def setCursor(self, _x, _y):
        return
    def printout(self, _m):
        return

try:
    lcd = LCD1602(16,2)
except OSError:
    lcd = NoLcd()

# Get Our Configuration
dmxrx_deviceaddress = config.dmx_address  # Our device Base DMX Address
dmxrx_devicechannels = config.dmx_channels  # How many channels we care about

# Environment Setup
gc.threshold(16384)  # Run Garbage collection everytime 16KB is allocated
alloc_emergency_exception_buf(512)  # Allocate Emergency Exception Buffer

def update_apa102_simple(grgbw_list):
    print("update called")
    # global_bright = int(grgbw_list[0] / 8)  # Valid 1-31, 0 = disable
    # pixels.customwrite(global_bright, grgbw_list[1], grgbw_list[3], grgbw_list[2], 1, 3)

def dmxstatuschange(status):
    if status == 0: # We are offline & timed-out
        print("Turning off LED Output")
        # pixels.clear()

# Configuring Modules - DMX Receiver
dmx = dmx512_rx.DMX(dmxrx_deviceaddress, dmxrx_devicechannels, 1)
dmx.set_updatefunction(update_apa102_simple)
dmx.set_statusfunction(dmxstatuschange)  # Not needed with full rainbow fallback

print("INFO: Starting Main Loop")
lcd.print_lcd("STARTING...")

# while True:
#     uasyncio.sleep(1)
    # if dmx.loop() == 0:  # If 0 we have been offline for an extended period
    #     if fullrainbow_refresh_ms < time.ticks_ms():
    #         fullrainbow_refresh_ms = time.ticks_ms() + 20
    #         pixels.fullrainbow_timer()
    #         rgb = pixels.fullrainbow_get()
    #         pixels.globalwrite(30, rgb[0], rgb[2], rgb[1])

async def main_loop():
    while True:
        dmx.loop()
        await uasyncio.sleep_ms(0)

if __name__ == "__main__":
    try:
        uasyncio.run(main_loop())
    except KeyboardInterrupt:
        print("clearing screen")
        lcd.print_lcd("STOPPED")
        utime.sleep(3)
        print("exiting")
