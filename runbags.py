#!/usr/bin/python3
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
import RPi.GPIO as GPIO
import sys
import time 

IR_INPUT_PIN = 6 
LED_OUTPUT_PIN = 25
PRINT_STATE_CHANGE = 0

print('Started with arguments:', str(sys.argv))

if 'player1' in sys.argv :
	outmsg = "/eos/fader/1/2/fire"
	print('Mode: Player 1')
else :
	outmsg = "/eos/fader/1/5/fire"
	print('Mode: Player 2')
outmsg = "/eos/fader/1/8/fire" 
# ignore for now
inimsg = "/eos/fader/1/config/10"

GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_INPUT_PIN, GPIO.IN)
GPIO.setup(LED_OUTPUT_PIN, GPIO.OUT)
osc_startup()

osc_udp_client("10.101.2.177", 53001, "hans_etcnomad")

try:
	msg = oscbuildparse.OSCMessage(outmsg, "", [])
	initmsg = oscbuildparse.OSCMessage(inimsg, "", {})
	osc_send(initmsg, "hans_etcnomad")

	def send_osc_on_change(channel) :
		if GPIO.input(channel):
			GPIO.output(LED_OUTPUT_PIN, False)
			if PRINT_STATE_CHANGE :
				print("off\n")
		else :
			GPIO.output(LED_OUTPUT_PIN, True)
			osc_send(msg, "hans_etcnomad")
			if PRINT_STATE_CHANGE :
				print("on\n")
	
	GPIO.add_event_detect(IR_INPUT_PIN, GPIO.BOTH, callback=send_osc_on_change, bouncetime=1)

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
