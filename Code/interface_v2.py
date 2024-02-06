import machine
import utime
from ssd1306 import SSD1306_I2C
from writer import Writer
import freesans30
import time
from rotary_irq_rp2 import RotaryIRQ


#Initialize connection to OLED display
#sda=machine.Pin(20)
#scl=machine.Pin(21)

#i2c=machine.I2C(0, sda=sda, scl=scl, freq=400000)	#Establish I2C comm

#oled = SSD1306_I2C(128, 32, i2c)					#Provide screen size
#wrt = Writer(oled, freesans30)						#Adjust font size

#Find saved frequency and set that to default frequency
file = open("saved_frequency.txt")					#Open file
default_frequency = int(file.read())
file.close()										#Must close to write on later

#Initialize variables
half_freq_status = False							#State of half-freq button
double_freq_status = False							#State of double-freq button
reset_freq_status = False							#State of reset freq button
freq_change = True									#Indicator for freq changed
save_freq_status = False							#State for saving frequency protocol
save_button_depress_time = 0
save_button_status = False
written_to_file = False
savetext_display_time = 0
max_frequency = 20000 #max allowable frequency [Hz]
min_frequency = 60 #min freq [Hz]
frequency = default_frequency						#Set frequency to default frequency when boot
debounce_time = 0									#Init debounce time token variable
debounce_dura = 300									#ms of debounce duration, increase if bouncing still happens

#Initialize the rotary encoder
r = RotaryIRQ(pin_num_clk=12,
              pin_num_dt=13,
              min_val=0,
              reverse = True,
              range_mode=RotaryIRQ.RANGE_UNBOUNDED)
val_old = r.value()									#Read current valuem, set as old value

#Initialize buttons connections
button_half_freq = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
button_double_freq = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
button_reset_freq = machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP)
pin_sig = machine.PWM(machine.Pin(18))

#Define interrupt functions
def half_freq_int_handler(pin):						#Int for half freq button
    global half_freq_status
    half_freq_status = True
    
def double_freq_int_handler(pin):					#Int for double freq button
    global double_freq_status
    double_freq_status = True

def reset_freq_int_handler(pin):					#Int for reset freq button
    global reset_freq_status
    reset_freq_status = True

#Initialize interrupt request
button_half_freq.irq(trigger=machine.Pin.IRQ_FALLING, handler=half_freq_int_handler)
button_double_freq.irq(trigger=machine.Pin.IRQ_FALLING, handler=double_freq_int_handler)
button_reset_freq.irq(trigger=machine.Pin.IRQ_FALLING, handler=reset_freq_int_handler)

#Main function
while True:
    #Half freq protocol
    if half_freq_status == True:
        if (time.ticks_ms()-debounce_time) > debounce_dura:
            debounce_time = time.ticks_ms()
            frequency = int(frequency/2)
            if frequency < min_frequency:
                frequency = min_frequency
            freq_change = True
            print("half freq")
        half_freq_status = False
        
    #Double freq protocol
    if double_freq_status == True:
        if (time.ticks_ms()-debounce_time) > debounce_dura:
            debounce_time = time.ticks_ms()
            frequency = int(frequency*2)
            if frequency > max_frequency:
                frequency = max_frequency
            freq_change = True
            print("double freq")
        double_freq_status = False
        
    #Reset freq protocol
    if reset_freq_status == True:
        if (time.ticks_ms()-debounce_time) > debounce_dura:
            debounce_time = time.ticks_ms()
            save_button_depress_time = time.ticks_ms()
            save_button_status = True    
        reset_freq_status = False
    
    if save_button_status == True and (time.ticks_ms()-save_button_depress_time) > 50:
            if button_reset_freq.value() == 1:
                frequency = default_frequency
                freq_change = True
                save_button_status = False
                print("reset freq")
            else:
                if (time.ticks_ms()-save_button_depress_time) > 2000:
                    save_freq_status = True
                    save_button_status = False
                    written_to_file = False
                    print("freq saved")
    
    if save_freq_status == True:
        if written_to_file == False:
            file = open("saved_frequency.txt", "w")
            file.write(str(frequency))
            file.close()
            written_to_file = True
            default_frequency = frequency
            #oled.fill(0)
            #Writer.set_textpos(oled, 0, 0)
            #wrt.printstring("SAVED")
            #oled.show()
            savetext_display_time = time.ticks_ms()
        
        if (time.ticks_ms()-savetext_display_time) > 2000:
            save_freq_status = False
            freq_change = True        
        
    val_new = r.value()								#Update value from rotary encoder
    #Update rotary encoder values
    if val_old != val_new:
        frequency = frequency + (val_new - val_old)
        val_old = val_new
        freq_change = True
    
    if freq_change == True:
        freq_change = False
        #Change the control signal
        pin_sig.freq(frequency)
        pin_sig.duty_u16(30000)
        
        #OLED display update when frequency is updated
        #oled.fill(0)
        #Writer.set_textpos(oled, 0, 0)
        #wrt.printstring(str(frequency))
        #oled.show()
    