#!/usr/bin/python3
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
import RPi.GPIO as GPIO
import sys
import time 

IR_INPUT_PIN = 6 
LED_OUTPUT_PIN = 25
PRINT_STATE_CHANGE = 0
SEND_ON_UP_EDGE_INSTEAD = 1
MS_BOUNCE_TIME = 500

print('Started with arguments:', str(sys.argv))

if 'player1' in sys.argv :
	outmsg = "/eos/fader/1/2/fire"
	print('Mode: Player 1')
else :
	outmsg = "/eos/fader/1/5/fire"
	print('Mode: Player 2')

if SEND_ON_UP_EDGE_INSTEAD :
	print('Edge: UP_EDGE')
else :
	print('Edge: DOWN_EDGE')

print('Bounce time (ms): ' + str(MS_BOUNCE_TIME))

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
			if SEND_ON_UP_EDGE_INSTEAD :
				osc_send(msg, "hans_etcnomad")
			if PRINT_STATE_CHANGE :
				print("off\n")
		else :
			GPIO.output(LED_OUTPUT_PIN, True)
			if not SEND_ON_UP_EDGE_INSTEAD :
				osc_send(msg, "hans_etcnomad")
			if PRINT_STATE_CHANGE :
				print("on\n")
	
	GPIO.add_event_detect(IR_INPUT_PIN, GPIO.BOTH, callback=send_osc_on_change, bouncetime=MS_BOUNCE_TIME)

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
