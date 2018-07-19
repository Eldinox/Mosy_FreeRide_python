import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time


    
url = "broker.mqttdashboard.com"
topic = "mosy/freeride"

#Pin Nummern
input_fr = 31 #frequenzen vom sensor gesendet    schwarzes kabel rote     seite
output1 = 33  #Enable                            blaues    kabel schwarze seite
output2 = 37  #s0                                gelbes    kabel schwarze seite
output3 = 35  #s1                                rotes     kabel schwarze seite
output4 = 29  #s2                                gelbes    kabel rote     seite
output5 = 24  #s3                                blaues    kabel rote     seite

#Initialisierungen von Variablen
global payload
payload = 'r'                #Payload das gesendet wird
global tornummer
tornummer = 1                #Nummer des naechsten erwarteten Tores
global gate
gate = 0                     #wenn gerade im Tor gate = 1

    
def scale(s0,s1):  
    #frequenzscaling
    #s0 s1
    #0  0  aus
    #0  1  2%
    #1  0  20%
    #1  1  100%
#s0 
	GPIO.output(output2, s0)
#s1
	GPIO.output(output3, s1)

    
def farbe(s2,s3):    
    #sensorauswahl
    #s2 s3
    #0  0  rot
    #0  1  blau
    #1  0  kein filter
    #1  1  gruen
#s2
	GPIO.output(output4, s2)
#s3
	GPIO.output(output5, s3)


def frequenz():  #bestimmt die Frequenz in Herz
	anzahl_flanken = 10  
	beginn = time.time()                           
	for i in range(0,anzahl_flanken,1):       
		GPIO.wait_for_edge(input_fr, GPIO.FALLING)        
	dauer = time.time() - beginn     
	frequenz = anzahl_flanken / dauer              
	frequenz = round(frequenz)    
	return frequenz    


def setup(): 
    #GPIO
    GPIO.setmode(GPIO.BOARD)

    #Pin Setup            #die Pins sind mit output1 usw. benannt siehe oben unter "Pin Nummern"
    GPIO.setup(input_fr, GPIO.IN) #in frequenz
    GPIO.setup(output1, GPIO.OUT) #out Enable Output 
    GPIO.output(output1, 0)
    GPIO.setup(output2, GPIO.OUT) #out S0
    GPIO.setup(output3, GPIO.OUT) #out S1
    GPIO.setup(output4, GPIO.OUT) #out S2
    GPIO.setup(output5, GPIO.OUT) #out S3
        
    scale(0,1) 
   

def loop(client):  
    
    global payload
    global tornummer
    global gate

    abstand = 600  #der Abstand beschreibt die Empfindlichkeit des Sensor, sodass er auf die LED reagiert, aber nicht auf Streulicht
    farbe(0,0)  #rot
    rot = frequenz()
    farbe(0,1)  #blau
    blau = frequenz()
    dif_r_b = abs(rot - blau)   #senden bei Ausschlag des Sensors
    if dif_r_b <= abstand:
        gate = 0
        return
   
    #bei Durchfahren des Tores, senden ueber mqtt an die App b beim ersten Tor, r beim zweiten Tor , g beim dritten Tor
    if dif_r_b > abstand :         
        if blau < rot :         #senden beim ersten und letzten Tor (payload = b)
            if  int(gate) == 0 and int(tornummer) != 2 :
                gate = 1                   # befindet sich im Tor, sendet deshalb nur einmal das payload
                if tornummer == 1 :            # wenn es das erste tor war
                    tornummer = 2              # markiert das naechste angenommene Tor (also Tor Nummer 2)
                    payload = 'b'
                    print('Start')
                else :
                    tornummer = 1              # wenn es das letzte Tor war geht er zurueck zum ersten Tor
                    payload = 'g'
                    print('Ende')
                #sende payload                 
                client.publish(topic , payload)

        if blau > rot :         #senden beim mittleren Tor (payload = r)
            if int(gate) == 0 and int(tornummer) == 2 :
                payload = 'r'
                print('Zwischen')
                gate = 1                   # befindet sich im Tor, sendet nur einmal das payload
                tornummer = 3              # markiert das naechste angenommene Tor (also Tor Nummer 3)  
                #sende payload
                client.publish(topic , payload)
    
        if tornummer == 1:      #wenn das letzte Tor durchfahren wurde wartet er 1 Sekunde bis ein neues Rennen beginnen kann
            time.sleep(1)
        
            

client = mqtt.Client()
client.connect(url, 1883, 60) 				#Connect
client.loop_start()

try:
    setup()

    while(1):
        loop(client)
        
except KeyboardInterrupt:
    print('  cleanup')

GPIO.cleanup()
client.loop_stop()
