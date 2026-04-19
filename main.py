from micropython import alloc_emergency_exception_buf
import gc
import dmx512_rx
import config
import LCD1602
import ws2812
import uasyncio
import utime

leds = [0,0,0,0,0,0]

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

# Get DMX Configuration
dmxrx_deviceaddress = config.dmx_address  # Our device Base DMX Address
dmxrx_devicechannels = config.dmx_channels  # How many channels we care about

# Environment Setup
gc.threshold(16384)  # Run Garbage collection everytime 16KB is allocated
alloc_emergency_exception_buf(512)  # Allocate Emergency Exception Buffer


def update(grgbw_list):
    global leds

    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout(" ".join(f"{value:03}" for value in grgbw_list[0:3]))
    lcd.setCursor(0, 1)
    lcd.printout(" ".join(f"{value:03}" for value in grgbw_list[3:]))
    leds = grgbw_list[0:6]


def dmxstatuschange(status):
    global leds

    if status == 0: # We are offline & timed-out
        print("Turning off LED Output")
        lcd.print_lcd("DISCONNECTED")
        for i in range(len(leds)): leds[i] = 0


# Configuring Modules - DMX Receiver
dmx = dmx512_rx.DMX(dmxrx_deviceaddress, dmxrx_devicechannels, 1)
dmx.set_updatefunction(update)
dmx.set_statusfunction(dmxstatuschange)  # Not needed with full rainbow fallback

print("INFO: Starting Main Loop")


async def main():

    ws2812.pixels_fill((0,0,0))
    await ws2812.pixels_show()
    while True:
        dmx.loop()
        ws2812.pixels_set(0,(leds[0],0,0))
        ws2812.pixels_set(1,(0,leds[1],0))
        ws2812.pixels_set(2,(0,0,leds[2]))
        ws2812.pixels_set(3,(leds[3],leds[3],0))
        ws2812.pixels_set(4,(0,leds[4],leds[4]))
        ws2812.pixels_set(5,(leds[5],0,leds[5]))
        await ws2812.pixels_show()


async def blank():

    ws2812.pixels_fill((0,0,0))
    await ws2812.pixels_show()


if __name__ == "__main__":
    try:
        uasyncio.run(main())
    except KeyboardInterrupt:
        uasyncio.run(blank())
        print("clearing screen")
        lcd.print_lcd("")
        utime.sleep(3)
        print("exiting")
