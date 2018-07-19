    #Quelle des Codes zum Ansteuern des Schrittmotors:
    #https://tutorials-raspberrypi.de/raspberry-pi-schrittmotor-steuerung-l293d-uln2003a/
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

url = "broker.mqttdashboard.com"
topic = "mosy/freeride"
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe(topic)
	print("Kameramotor connected")
    
GPIO.setmode(GPIO.BOARD)
#Schrittmotor horizontal
Pin1 = 40 # Motor1
Pin2 = 36 # Motor2
Pin3 = 32 # Motor3
Pin4 = 38 # Motor4
#Servomotor vertikal
Pin5 = 26 #Signal je nach Signallaenge rechts oder links


global istwert_h
istwert_h = int(255) #beim startwert sollte die kamera nach vorne gerichtet sein (512 Richtungsschritte)
global istwert_v
istwert_v = int(23) #24 werte von 0 bis 23


 #Schritte der Motoren im Urzeigersinn
StepCount = 8
Seq = list(range(0, StepCount))
Seq[0] = [1,0,0,0] #1      Nummern der angesprochenen Motoren
Seq[1] = [1,1,0,0] #12 
Seq[2] = [0,1,0,0] # 2  
Seq[3] = [0,1,1,0] # 23
Seq[4] = [0,0,1,0] #  3
Seq[5] = [0,0,1,1] #  34
Seq[6] = [0,0,0,1] #   4
Seq[7] = [1,0,0,1] #1  4    
    
#GPIO.setup
GPIO.setup(Pin1, GPIO.OUT)
GPIO.setup(Pin2, GPIO.OUT)
GPIO.setup(Pin3, GPIO.OUT)
GPIO.setup(Pin4, GPIO.OUT)
GPIO.setup(Pin5, GPIO.OUT)

         

def setStep(w1, w2, w3, w4): #setzt die Pins auf 1 oder 0 je nach Sequenz
    GPIO.output(Pin1, w1)
    GPIO.output(Pin2, w2)
    GPIO.output(Pin3, w3)
    GPIO.output(Pin4, w4)
 
def forward(delay, steps): #laeuft "steps" Anzahl an Schritten alle Sequenzen vorwaerts durch
    for i in range(steps):
        for j in range(StepCount):
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)
            
            
def backwards(delay, steps): #laeuft "steps" Anzahl an Schritten alle Sequenzen rueckwaerts durch
    for i in range(steps):
        for j in reversed(range(StepCount)):
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)
            
def on_message(client , userdata , msg):
	payload = msg.payload.decode('utf-8')
	global istwert_h
	global istwert_v    
	try:    
		g,r,sollwert_h,sollwert_v = payload.split()  #erwartet Eingabe im Format "sollwert_h sollwert_v" [soll_h leer soll_v]                                                                  # sollwert_h von 0 bis 511 (0° bis 360°)
                                             # sollwert_v von 0 bis 23 (x Schritte hoch und runter, noch ausprobieren)
                                                #g,r ist wichtig fuer die radbefehle
#kameradrehung im discovery-modus
		if str(sollwert_h) != 'RR':
    
#abfangen von werten ueber 90° drehung (ausgehend von ausgangsposition)
			if int(sollwert_h) < 128:
				sollwert_h = 128
			elif int(sollwert_h) > 383:
				sollwert_h = 383   
#reaktion von vertikaler bewegung            
			dif_v = abs(int(istwert_v) - int(sollwert_v))
          
            
           
			sollwert_h = round(int(sollwert_h))
			sollwert_v = round(int(sollwert_v))   
			dif_h = abs(istwert_h - sollwert_h) 
			dif_v = abs(istwert_v - sollwert_v)
#anzahl der drehungsstuecke werden festgelegt auf kleinsten vorkommenden wert --->variable "minimum"            
			minimum = 1
			if  0 < dif_h < dif_v :  
				minimum = dif_h
			elif 0 < dif_v < dif_h :
				minimum = dif_v
			if 23 < minimum  :
				minimum = 23          


                                  
                    
			for k in range (1,minimum+1,1): # k und l und miminum werden verwendet um zu stueckeln auf "minimum" schritte
    #horizontal
				if k<(minimum):                  # differenz in minimum schritte geteilt
					l = dif_h // (minimum) 
				else:
					l = dif_h//minimum + dif_h % (minimum)
					print('modulo ist',(dif_h % minimum))                    
				print(k,l)
				if sollwert_h > istwert_h :        
					for i in range(0,round(l),1) :                        
						delay = 1 #Verzoegerung zwischen 2 Wiederholungen --> je hoeher desto langsamer dreht er sich   
						steps = 1    #Anzahl der Wiederholungen aller Schritte/Sequenzen
						forward(int(delay) / 1000.0, int(steps))          
				elif sollwert_h < istwert_h :            
					for i in range(0,round(l),1) :       
						delay = 1 #Verzoegerung zwischen 2 Wiederholungen --> je hoeher desto langsamer dreht er sich   
						steps = 1    #Anzahl der Wiederholungen aller Schritte/Sequenzen
						backwards(int(delay) / 1000.0, int(steps))  
				else:
					print('Horizontale Position erreicht')                    

    #vertikal
				if dif_v > 1 :    #reaktion auf vertikalwert mit toleranz
					if istwert_v > round(sollwert_v): # rechtsdrehung wenn der wert groesser ist
							GPIO.output(Pin5, 1)
							time.sleep(0.002)

							GPIO.output(Pin5, 0)
							time.sleep(0.018)     
        
					if istwert_v < round(sollwert_v): # linksdrehung wenn der wert groesser ist
							GPIO.output(Pin5, 1)
							time.sleep(0.001)

							GPIO.output(Pin5, 0)
							time.sleep(0.019)        
        
					else:
						GPIO.output(Pin5, 0)    
						time.sleep(0.02)    


			istwert_v = sollwert_v     
			istwert_h = sollwert_h  
        
		else: #wenn RR in Befehl  

#dreht kamera in ausgangsposition 
#horizontal
			sollwert_h = 255
			if sollwert_h > istwert_h :  
				for i in range(istwert_h,sollwert_h,+1) :
					delay = 1  
					steps = 1    
					forward(int(delay) / 1000.0, int(steps))          
			elif sollwert_h < istwert_h :            
				for i in range(istwert_h,sollwert_h,-1) :       
					delay = 1 
					steps = 1    
					backwards(int(delay) / 1000.0, int(steps))   
			else:
				print('unbekannter Befehl')
			istwert_h = sollwert_h   
            
			#vertikal
			sollwert_v = 23
			dif_v = abs(istwert_v - sollwert_v)    
			if istwert_v > sollwert_v: # rechtsdrehung wenn der sollwert groesser ist
				for i in range(0,dif_v,1) :
					GPIO.output(Pin5, 1)
					time.sleep(0.002)

					GPIO.output(Pin5, 0)
					time.sleep(0.018) 
                    
					time.sleep(0.040)
                    
			if istwert_v < sollwert_v: # linksdrehung wenn der sollwert kleiner ist
				for i in range(0,dif_v,1) :
					GPIO.output(Pin5, 1)
					time.sleep(0.001)

					GPIO.output(Pin5, 0)
					time.sleep(0.019)  
                    
					time.sleep(0.040)  
                    
			else:
				GPIO.output(Pin5, 0)    
				time.sleep(0.02)    
			istwert_v = sollwert_v 
    
	except ValueError as error: #im fall eines errors: schreiben der fehlermeldung
		print(error)    
    
#Hier gehts los
client = mqtt.Client() 						#Client object
client.on_connect = on_connect 		#Callbacks registrieren 
client.on_message = on_message

client.connect(url, 1883, 60) 				#Connect
client.loop_start()

cmd = input('>')
#dreht kamera in ausgangsposition 
#horizontal
sollwert_h = 255
if sollwert_h > istwert_h :  
	for i in range(istwert_h,sollwert_h,+1) :
		delay = 1  
		steps = 1    
		forward(int(delay) / 1000.0, int(steps))      
elif sollwert_h < istwert_h :            
	for i in range(istwert_h,sollwert_h,-1) :       
		delay = 1 
		steps = 1    
		backwards(int(delay) / 1000.0, int(steps))        
else:
	print('unbekannter Befehl')
istwert_h = sollwert_h    

#vertikal
sollwert_v = 23
dif_v = abs(istwert_v - sollwert_v) 
if istwert_v > sollwert_v: # rechtsdrehung wenn der sollwert groesser ist
	for i in range(0,dif_v,1) :
		GPIO.output(Pin5, 1)
		time.sleep(0.002)

		GPIO.output(Pin5, 0)
		time.sleep(0.018)     

		time.sleep(0.040) 
        
if istwert_v < sollwert_v: # linksdrehung wenn der sollwert kleiner ist
	for i in range(0,dif_v,1) :
		GPIO.output(Pin5, 1)
		time.sleep(0.001)
		GPIO.output(Pin5, 0)
		time.sleep(0.019)
        
		time.sleep(0.040)
        
else:
	GPIO.output(Pin5, 0)    
	time.sleep(0.02)    
istwert_v = sollwert_v 
        
GPIO.cleanup() #beendet gpio einstellungen

client.loop_stop()