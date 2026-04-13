#STANDARD VERSION - Simple LED Output of a single color on a single APA102 LED string
from micropython import mem_info, alloc_emergency_exception_buf
import gc
import dmx512_rx
import config
import time
import LCD1602
import ws2812

# mock class should the LCD not be detected
class NoLcd:
    def print_lcd(self, _m):
        return
    def setCursor(self, _x, _y):
        return
    def printout(self, _m):
        return

try:
    lcd = LCD1602.LCD1602(16,2)
except OSError:
    lcd = NoLcd()

# Get Our Configuration
dmxrx_deviceaddress = config.dmx_address  # Our device Base DMX Address
dmxrx_devicechannels = config.dmx_channels  # How many channels we care about
ws2812_numleds = config.ws2812_numleds

# Environment Setup
gc.threshold(16384)  # Run Garbage collection everytime 16KB is allocated
alloc_emergency_exception_buf(512)  # Allocate Emergency Exception Buffer

def update(grgbw_list):

    
    lcd.clear()
    
    lcd.setCursor(0, 0)
    lcd.printout(" ".join(f"{value:03}" for value in grgbw_list[0:3]))
    
    lcd.setCursor(0, 1)
    lcd.printout(" ".join(f"{value:03}" for value in grgbw_list[3:]))



def dmxstatuschange(status):
    if status == 0: # We are offline & timed-out
        print("Turning off LED Output")
        pixels.clear()


# Configuring Modules - DMX Receiver
dmx = dmx512_rx.DMX(dmxrx_deviceaddress, dmxrx_devicechannels, 1)
dmx.set_updatefunction(update)
# dmx.set_statusfunction(dmxstatuschange)  # Not needed with full rainbow fallback

print("INFO: Starting Main Loop")
while True:
    dmx.loop()
