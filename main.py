from micropython import alloc_emergency_exception_buf
import gc
import dmx512_rx
import config
import LCD1602
import ws2812
import uasyncio
import utime
import machine

channels = [0,0,0,0,0,0]

LED_PIN = const(17)
LED_DUTY_CYCLE = const(5000)  # PWM rate, out of 65535
LED_FREQUENCY = const(5000)  # PWM frequency, in Hz

led = machine.PWM(machine.Pin(LED_PIN, machine.Pin.OUT))
led.freq(LED_FREQUENCY)

# mock class should the LCD not be detected
class NoLcd:
    def print_lcd(self, _m, _blank=True):
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
    global channels 
    lcd.print_lcd(" ".join(f"{value:03}" for value in grgbw_list[0:3])+"     "+" ".join(f"{value:03}" for value in grgbw_list[3:6]), False)
    channels = grgbw_list[0:6]


def dmxstatuschange(status):
    global channels

    if status == 0: # We are offline & timed-out
        print("Turning off LED Output")
        lcd.print_lcd("DISCONNECTED")
        for i in range(len(channels)): channels[i] = 0


# Configuring Modules - DMX Receiver
dmx = dmx512_rx.DMX(dmxrx_deviceaddress, dmxrx_devicechannels, 1)
dmx.set_updatefunction(update)
dmx.set_statusfunction(dmxstatuschange)  # Not needed with full rainbow fallback

print("INFO: Starting Main Loop")

async def blank():

    ws2812.pixels_fill((0,0,0))
    await ws2812.pixels_show()
    
async def pattern1():
    try:
        while True:
            ws2812.pixels_fill((0,255,0))
            await ws2812.pixels_show()
            await uasyncio.sleep_ms(2000)
            ws2812.pixels_fill((255,0,0))
            await ws2812.pixels_show()
            await uasyncio.sleep_ms(2000)
    except uasyncio.CancelledError:
        await blank()


async def pattern2():
    try:
        while True:
            ws2812.pixels_fill((0,0,255))
            await ws2812.pixels_show()
            await uasyncio.sleep_ms(2000)
            ws2812.pixels_fill((0,255,255))
            await ws2812.pixels_show()
            await uasyncio.sleep_ms(2000)
    except uasyncio.CancelledError:
        await blank()

async def pattern3():
    try:
        while True:
            ws2812.pixels_fill((255,0,255))
            await ws2812.pixels_show()
            await uasyncio.sleep_ms(2000)
            ws2812.pixels_fill((255,255,0))
            await ws2812.pixels_show()
            await uasyncio.sleep_ms(2000)
    except uasyncio.CancelledError:
        await blank()

async def led_flash():
    try:
        print("flasher running")
        start_time = utime.time()
        while True:
            while utime.time() < start_time + 1:
                await uasyncio.sleep(0.05)
            led.duty_u16(LED_DUTY_CYCLE)
            await uasyncio.sleep(0.02)
            led.duty_u16(0)
            start_time += 3
    except uasyncio.CancelledError:
        pass

async def main():
    currentpattern = None
    currenttask = None
    global channels
    await blank()
    while True:
        dmx.loop()

        async def cancel(currenttask):
            if currenttask:
                currenttask.cancel()
                await currenttask
                print("Task canceled")

        if 64 < channels[0] < 127 and currentpattern != 1:
            await cancel(currenttask)
            currenttask = uasyncio.create_task(pattern1())
            print("Task 1 created")
            currentpattern = 1

        if 128 < channels[0] < 191 and currentpattern != 2:
            await cancel(currenttask)
            currenttask = uasyncio.create_task(pattern2())
            print("Task 2 created")
            currentpattern = 2
        
        if 192 < channels[0] < 256 and currentpattern != 3:
            await cancel(currenttask)
            currenttask = uasyncio.create_task(pattern3())
            print("Task 3 created")
            currentpattern = 3

        if channels[0] <= 63 and currenttask:
            await cancel(currenttask)
            currenttask = None
            currentpattern = None

        await uasyncio.sleep(0)


if __name__ == "__main__":
    try:
        uasyncio.create_task(led_flash())
        uasyncio.run(main())
    except KeyboardInterrupt:
        uasyncio.run(blank())
        print("clearing screen")
        lcd.print_lcd("")
        utime.sleep(3)
        print("exiting")
