# coding: utf8
""" Ma maison intelligente - Objet : 

    Envoi des données
    vers le serveur MQTT
"""

from machine import Pin, I2C, reset
from time import sleep, time
from ubinascii import hexlify
from network import WLAN

CLIENT_ID = "bureau"

# Utiliser IP  si le Pi en adresse fixe
MQTT_SERVER ="192.168.1.159"

MQTT_USER = "dimitri"
MQTT_PSWD = "36773677"

# redemarrage auto apres erreur
ERROR_REBOOT_TIME =3600

# --- Demarrage conditionnel ---
runapp = Pin(12, Pin.IN, Pin.PULL_UP)
led = Pin(2, Pin.OUT)
led.value(1) # eteindre

def led_error( step ):
    global led
    t = time()
    while ( time()-t ) < ERROR_REBOOT_TIME:
        for i in range( 20 ):
            led.value( not(led.value()))
            sleep(0.100)
        led.value(1) #eteindre
        sleep(1)
        # clignote nbr fois
        for i in range ( step ):
            led.value(0)
            sleep(0.5)
            led.value(1)
            sleep(0.5)
        sleep(1)
    # Re-start the ESP
    reset()

if runapp.value() !=1:
    from sys import exit
    exit(0)

led.value(0) # allumer

# --- Programme Principal ---
from umqtt.simple import MQTTClient
try:
    q = MQTTClient( client_id = CLIENT_ID, server =
        MQTT_SERVER, user = MQTT_USER, password = 
        MQTT_PSWD )
    if q.connect() !=0:
        led_error( step=1 )
except Exception as e:
    print( e )
    # chek MQTT_SERVER, MQTT_USER, MQTT_PSWD
    led_error( step=2 )

try:
    from bme_tiny import BME280
    #reduir de 4 bytes ce code ???
except Exception as e:
    print( e )
    led_error( step=3)

i2c = I2C (sda=Pin(5), scl=Pin(14),freq=10000)

#creer senseurs
try:
    bmp= BME280(i2c=i2c)
except Exception as e:
    print( e )
    led_error( step =4 )

try:
    # annonce connexion objet
    sMac = hexlify( WLAN().config('mac'),':' ).decode()
    q.publish("connect/%s"% CLIENT_ID, sMac)
except Exception as e:
    print( e )
    led_error( step=5 )

import uasyncio as asyncio

def capture_15sec():
    """ Execute pour capturer des donnees toutes
    les 15sec """
    global q
    global bmp

    #bmp280 -senseur pression/temperature
    #capturer les valeurs sous format texte
    t = bmp.temperature
    p = bmp.pressure
    #h = bmp.humidity
    print(t)
    q.publish("maison/rdc/bureau/temp", t)
    q.publish("maison/rdc/bureau/pathm", p)

def heartbeat():
    """led eteinte 200ms toutes les 10 sec"""
    sleep( 0.2 )

async def run_every ( fn, min=1, sec=None):
    """ Execute une fonction fn toutes les minutes ou
    secondes"""
    global led
    wait_sec = sec if sec else min*60
    while True:
        # eteindre pendant envoi/traitement
        led.value(1)
        fn()
        led.value(0)
        await asyncio.sleep( wait_sec )
async def run_app_exit():
    """ fin d execution lorsque la fonction quitte """
    global runapp
    while runapp.value()==1:
        await asyncio.sleep(10)
    return

loop = asyncio.get_event_loop()
loop.create_task( run_every(capture_15sec, sec=15))
loop.create_task( run_every(heartbeat, sec=10))
try:
    loop.run_until_complete( run_app_exit() )
except Exception as e :
    print( e )
    led_error( step=0)

loop.close()
led.value(1) # eteindre
print( "Fin!")
