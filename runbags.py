#!/usr/bin/python3
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
import RPi.GPIO as GPIO
import sys
import time 

#### options ####
# input pin for ir sensor (white wire)
IR_INPUT_PIN = 6 

# output pin for indicator LED
LED_OUTPUT_PIN = 25

# print changes to stdout
PRINT_STATE_CHANGE = 1

# time in seconds to suppress duplicate messages. a second closure outside this time is ignored
MS_BOUNCE_TIME = .50

# ip address of target device
OSC_TARGET_IP = "10.101.2.177"

# udp port for target device to receive OSC
OSC_TARGET_PORT = 53001


print('Started with arguments:', str(sys.argv))

if 'player1' in sys.argv :
	outmsg = "/eos/fader/1/2/fire"
	print('Mode: Player 1')
else :
	outmsg = "/eos/fader/1/5/fire"
	print('Mode: Player 2')

print('Bounce time (ms): ' + str(MS_BOUNCE_TIME))


# init message for Eos - map same fader config as wings/virtual module
initmsg_str = "/eos/fader/1/config/10"

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_INPUT_PIN, GPIO.IN)
GPIO.setup(LED_OUTPUT_PIN, GPIO.OUT)

# OSC 
osc_startup()
osc_udp_client(OSC_TARGET_IP, OSC_TARGET_PORT, "primary_osc_device")

# Score variables
score_active = False
activation_time = time.perf_counter()


try:
	# startup
	initmsg = oscbuildparse.OSCMessage(initmsg_str, "", {})
	osc_send(initmsg, "primary_osc_device")

	msg = oscbuildparse.OSCMessage(outmsg, "", [])

	# callback for GPIO 
	def send_osc_on_change(channel) :
		global activation_time
		global score_active

		# open = clear path on IR sensor
		if GPIO.input(channel):
			GPIO.output(LED_OUTPUT_PIN, False)
			activation_time = time.perf_counter()
			score_active = False
			osc_send(msg, "primary_osc_device")
			if PRINT_STATE_CHANGE :
				print("off\n")

		# closed = sensor blocked - possible score!
		else :
			if(time.perf_counter() - activation_time > MS_BOUNCE_TIME) :
				score_active = True
				GPIO.output(LED_OUTPUT_PIN, True)
			if PRINT_STATE_CHANGE :
				print("on\n")
	
	# add modest 50ms bounce time to GPIO lib - problem is that both down and up edge are absorbed
	# by the library, so we miss the up edge when it happens. allowing 51ms to MS_BOUNCE_TIME ms
	# to clear the sensor
	GPIO.add_event_detect(IR_INPUT_PIN, GPIO.BOTH, callback=send_osc_on_change, bouncetime=50)

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
