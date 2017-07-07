#!/usr/bin/python3
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
import RPi.GPIO as GPIO
import sys
import time 

print('Started with arguments:', str(sys.argv))
print('Mode: ', sys.argv[1])

if sys.argv[1] == 'player1' :
	outmsg = "/eos/fader/1/2/fire"
else :
	outmsg = "/eos/fader/1/5/fire"

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN)
GPIO.setup(25, GPIO.OUT)

osc_startup()
osc_udp_client("10.101.2.177", 53001, "hans_etcnomad")

try:
	msg = oscbuildparse.OSCMessage(outmsg, "", [])

	def send_osc_on_change(channel) :
		if GPIO.input(channel):
			GPIO.output(25, False)
		else :
			GPIO.output(25, True)
			osc_send(msg, "hans_etcnomad")
	
	GPIO.add_event_detect(27, GPIO.BOTH, callback=send_osc_on_change, bouncetime=1)

	while True:
		osc_process()
		time.sleep(0.01)
except KeyboardInterrupt:
	print("\nExiting")
except:
	e = sys.exec_info()[0]
	write_to_page("Error: %s" % e)
	print("\nExiting for other reason")
finally:
	osc_terminate()
	GPIO.cleanup()
