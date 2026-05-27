# Buttons info

Python demo for reading buttons
```python
if not buttons[0].value() and utime.ticks_diff(utime.ticks_ms(), pressed) > debounce_ms:
    lcd.print_lcd("BUTTON 0")
    print("BUTTON 0")
if not buttons[1].value() and utime.ticks_diff(utime.ticks_ms(), pressed) > debounce_ms:
    lcd.print_lcd("BUTTON 1")
    print("BUTTON 1")
if not buttons[2].value() and utime.ticks_diff(utime.ticks_ms(), pressed) > debounce_ms:
    lcd.print_lcd("BUTTON 2")
    print("BUTTON 2")
if not buttons[3].value() and utime.ticks_diff(utime.ticks_ms(), pressed) > debounce_ms:
    lcd.print_lcd("BUTTON 3") 
    print("BUTTON 3")
```

| Colour | Index | GPIO |
|---|---|---|
|Blue| 0| 18|
|White|1|19|
|Yellow|2|20|
|Red|3|21|