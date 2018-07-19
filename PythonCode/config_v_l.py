import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(26, GPIO.OUT) 
GPIO.output(26, False)


for i in range(0, 2):
	GPIO.output(26, 1)
	time.sleep(0.001)

	GPIO.output(26, 0)
	time.sleep(0.019)
    

GPIO.output(26, False)
GPIO.cleanup()