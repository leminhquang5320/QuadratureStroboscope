from machine import PWM, Pin

p18 = PWM(Pin(18))

p18.freq(16)
p18.duty_u16(30000)