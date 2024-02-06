import machine
import utime

sda=machine.Pin(20)
scl=machine.Pin(21)

i2c=machine.I2C(0, sda=sda, scl=scl, freq=400000)

from ssd1306 import SSD1306_I2C
oled = SSD1306_I2C(128, 32, i2c)

oled.text('Welcome to the', 0, 0)
oled.text('Pi Pico', 0, 10)
oled.text('Display Demo', 0, 20)
oled.show()
utime.sleep(4)

oled.fill(1)
oled.show()
utime.sleep(2)
oled.fill(0)
oled.show()

while True:
    oled.text("Hello World", 0, 0)
    for i in range (0,164):
        oled.scroll(1, 0)
        oled.show()
        utime.sleep(0.01)