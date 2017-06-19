#!/usr/bin/python
from OSC import *
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN)
GPIO.setup(25, GPIO.OUT)

c = OSCStreamingClient()
c.connect(('10.101.2.177',3032))

def eos_out_handler(addr, tags, stuff, source):
	1	
c.addMsgHandler('default', eos_out_handler)
c.sendOSC(OSCMessage("/eos/fader/1/config/10"))

def send_osc_on_change(channel) :
	if GPIO.input(channel):
		# c.sendOSC(OSCMessage(""))
		GPIO.output(25, False)
	else :
		c.sendOSC(OSCMessage("/eos/fader/1/2/fire"))
		GPIO.output(25, True)

GPIO.add_event_detect(27, GPIO.BOTH, callback=send_osc_on_change, bouncetime=1)

input()

quit()
