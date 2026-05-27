from micropython import alloc_emergency_exception_buf
import gc
import dmx512_rx
import LCD1602
import ws2812
import uasyncio
import utime
import machine
import json

channels = [0,0,0,0,0,0]

LED_PIN = const(17) # led flasher
LED_DUTY_CYCLE = const(5000)  # PWM rate, out of 65535
LED_FREQUENCY = const(5000)  # PWM frequency, in Hz

led = machine.PWM(machine.Pin(LED_PIN, machine.Pin.OUT))
led.freq(LED_FREQUENCY)

buttons = []
buttons.append(machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP))
buttons.append(machine.Pin(19, machine.Pin.IN, machine.Pin.PULL_UP))
buttons.append(machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_UP))
buttons.append(machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP))


debounce_ms = const(100)

# mock class should the LCD not be detected
class NoLcd:
    def clear(self):
        return
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

brightness = 255

gamma = 2.8
brightness_lut = [int(((i / 255.0) ** gamma) * 255.0) for i in range(256)]

def scale_color(rgb):
    global brightness
    return tuple(((c * brightness_lut[brightness])//255) for c in rgb)

def write_json():
    global dmxchannel
    with open('dmxchannel.json', 'w') as f:
        json.dump(dmxchannel, f)
        
def read_json():
    global dmxchannel
    with open('dmxchannel.json') as f:
        dmxchannel = json.load(f) 

dmxchannel = {"dmxchannel":0}
try:
    read_json()
except:
    write_json()

# Get DMX Configuration
dmxrx_deviceaddress = dmxchannel["dmxchannel"] # Our device Base DMX Address
dmxrx_devicechannels = 2 # How many channels we care about



lcd.print_lcd(f"CHANNEL: {dmxchannel["dmxchannel"]}" + "      STARTING...",False)
print("DMX CHANNEL IS:", dmxchannel["dmxchannel"])


utime.sleep(2)


# Environment Setup
gc.threshold(16384)  # Run Garbage collection everytime 16KB is allocated
alloc_emergency_exception_buf(512)  # Allocate Emergency Exception Buffer


def update(grgbw_list):
    global channels 
    #lcd.print_lcd(" ".join(f"{value:03}" for value in grgbw_list[0:3])+"     "+" ".join(f"{value:03}" for value in grgbw_list[3:6]), False)
    channels = grgbw_list[0:2]


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
            starttime = utime.ticks_ms()

            while utime.ticks_diff(utime.ticks_ms(),starttime) < 2000:
                ws2812.pixels_fill(scale_color((0,255,0)))
                await ws2812.pixels_show()

            starttime = utime.ticks_ms()

            while utime.ticks_diff(utime.ticks_ms(),starttime) < 2000:
                ws2812.pixels_fill(scale_color((255,0,0)))
                await ws2812.pixels_show()
            
    except uasyncio.CancelledError:
        await blank()


async def pattern2():
    try:
        while True:

            starttime = utime.ticks_ms()

            while utime.ticks_diff(utime.ticks_ms(),starttime) < 2000:
                ws2812.pixels_fill(scale_color((0,0,255)))
                await ws2812.pixels_show()
            
            starttime = utime.ticks_ms()

            while utime.ticks_diff(utime.ticks_ms(),starttime) < 2000:
                ws2812.pixels_fill(scale_color((0,255,255)))
                await ws2812.pixels_show()
    except uasyncio.CancelledError:
        await blank()

async def pattern3():
    try:
        while True:
            starttime = utime.ticks_ms()

            while utime.ticks_diff(utime.ticks_ms(),starttime) < 2000:
                ws2812.pixels_fill(scale_color((255,0,255)))
                await ws2812.pixels_show()

            starttime = utime.ticks_ms()

            while utime.ticks_diff(utime.ticks_ms(),starttime) < 2000:
                ws2812.pixels_fill(scale_color((255,255,0)))
                await ws2812.pixels_show()

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

async def setup():
    dummydmxrxchannel = dmxrx_deviceaddress
    await blank()

    starttime = utime.ticks_ms()

    while buttons[3].value() or utime.ticks_diff(utime.ticks_ms(),starttime)<debounce_ms:
        lcd.print_lcd("SETUP   EXIT=RED"+"YEL = CHANGE C",False)

        if not buttons[2].value():
            starttime = utime.ticks_ms()
            while buttons[3].value() or utime.ticks_diff(utime.ticks_ms(),starttime)<debounce_ms:
                lcd.print_lcd(f"CHANNEL:        {dummydmxrxchannel:03}     EXIT=RED",False)

                if not buttons[0].value() and utime.ticks_diff(utime.ticks_ms(), starttime) > debounce_ms:
                    starttime = utime.ticks_ms()
                    dummydmxrxchannel -= 1
                    utime.sleep(0.2)

                if not buttons[1].value() and utime.ticks_diff(utime.ticks_ms(), starttime) > debounce_ms:
                    starttime = utime.ticks_ms()
                    dummydmxrxchannel += 1
                    utime.sleep(0.2)

                if dummydmxrxchannel > 510: # upper bound
                    dummydmxrxchannel = 510
                elif dummydmxrxchannel < 0: # lower bound
                    dummydmxrxchannel = 0

            lcd.print_lcd("SETUP   EXIT=RED"+"YEL = CHANGE C",False)
            starttime = utime.ticks_ms()
            while not buttons[3].value() or utime.ticks_diff(utime.ticks_ms(),starttime)<debounce_ms:
                pass

    lcd.print_lcd("RUNNING         SETUP:PRESS BLUE",False)
    return


async def main():
    global channels, brightness
    currentpattern = None
    currenttask = None
    starttime = utime.ticks_ms()
    lcd.print_lcd("RUNNING         SETUP:PRESS BLUE",False)
    await blank()
    while True:
        dmx.loop()
        
        brightness = channels[1]

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

        if not buttons[0].value() and utime.ticks_diff(utime.ticks_ms(), starttime) > debounce_ms:
            await cancel(currenttask)
            currenttask = None
            currentpattern = None
            await setup()

        await uasyncio.sleep(0)


if __name__ == "__main__":
    try:
        uasyncio.create_task(led_flash())
        uasyncio.run(main())
    except KeyboardInterrupt:
        uasyncio.run(blank())
        print("clearing screen")
        lcd.print_lcd("")
        utime.sleep(1)
        print("exiting")
