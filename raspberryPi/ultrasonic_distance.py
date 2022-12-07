#Libraries;
import RPi.GPIO as GPIO
import time
import pygame
import math
import random

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import json

ENDPOINT = "au81yut9o46cd-ats.iot.us-east-2.amazonaws.com"
CLIENT_ID = "testDevice"
PATH_TO_CERTIFICATE = "certs/dev_certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "certs/private_key.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "certs/AmazonRootCA1.pem"
MESSAGE = '{"distance": 100}'
TOPIC = "esp8266/pub"
RANGE = 20

running = True
drawI = 0
devProximity = 100
currentSound = "0.ogg"
machineSound = "2.ogg"
soundLen = 0

# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERTIFICATE,
            pri_key_filepath=PATH_TO_PRIVATE_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
# Make the connect() call
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
print("now set pins")

def sendMessage(dist):
    message = {"distance" : dist}
    mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
    print("published")

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    StartTime = time.time()
    StopTime = time.time()
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
        #       print("stop recording")
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def preload():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(currentSound)
    mSound = pygame.mixer.Sound(machineSound)
    a = pygame.mixer.Sound(currentSound)
    soundLen = a.get_length()
    return mSound, soundLen

def soundJump(sound):
    start = random.uniform(0, soundLen)
    pygame.mixer.music.play(-1, start, 20)

def soundJumpWithDuration(sound, duration):    
    ms = int(duration*1000)
    mSound.play(maxtime=ms)

def playMachineSound(glitchPerc):
    start = random.uniform(0, soundLen)
    duration = soundLen - start

    machineDuration = duration * (glitchPerc * 0.01)

    soundJump(currentSound)
    soundJumpWithDuration(machineSound, machineDuration)

def getProximityFromDev(dist):
    if dist > 100:
        return 0
    else:
        return 100 - dist 

mSound, soundLen = preload()
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            glitchPerc = getProximityFromDev(dist)
            if glitchPerc == 0:
                division = 100
            else:
                division = math.floor(100/glitchPerc)
            
            if drawI%division==0 and glitchPerc < 51:
                soundJump(currentSound)
            elif glitchPerc > 50:
                glitchPercNew = glitchPerc - 50
                divisionNew = 2*math.floor(100/glitchPercNew)
                if drawI%divisionNew==0:
                   playMachineSound(glitchPercNew)
    
            drawI+=1
            drawI = drawI%100

            print ("Measured Distance = %.1f cm" % dist)
            sendMessage(dist)
            time.sleep(.1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
