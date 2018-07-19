import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

url = "broker.mqttdashboard.com"
topic = "mosy/freeride"
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe(topic)
	print("Raeder connected")

    
def on_message(client , userdata , msg):
	payload = msg.payload.decode('utf-8')
#erwartet payload im Format "100 75" (g r) gibt r ist Richtung, g ist Geschwindigkeit; benoetigt alle angaben
#g steht fuer die Geschwindigkeit; r ist der Protentsatz der Geschwindigkeit fuer die Richtung
#moegliche Eingaben: [g,r] g = 0 bis 100; r = 0 bis 100 (50=leer 0 bis 49 = links&rueckwaerts 51 bis 100 = rechts&vorwaerts)
#soll_h,soll_v sind kamerabefehle die hier nicht relevant sind
	try:
		g,r,soll_h,soll_v = payload.split() 
		takt = 0.0095  #Taktung von 9,5ms
		wiederholungen = 20    #momentan 190ms durch 10 wiederholungen   
		g = int(g)
		r = int(r)
		r2 = (r-50)*2
		g2 = (g-50)*2           
		m1 = round((abs(int(g2))-(abs(int(g2))*abs(int(r2))*0.01))*0.01*takt,4) #g-g*r/100 -->prozent der zeit, in der alle Motoren angesteuert werden #gerundet auf 4 Nachkommastellen
		m2 = round((abs(int(g2))*abs(int(r2))*0.01)*0.01*takt,4) #g*r/100 -->Prozent der Zeit, in der eine Seite angesteuert wird          
		m3 = round((100-abs(int(g2)))*0.01*takt,4) #100-g -->Prozent der Zeit, in der alles im leerlauf ist
		print(g , r)  
	except ValueError as error: #im fall eines errors:leerlauf
		print(error)
		takt = 0.01
		wiederholungen = 1    #momentan 10ms durch 1 wiederholung           
		g = 0
		r = 0 
		g2 = 0
		r2 = 0         
		m1 = round((abs(int(g2))-(abs(int(g2))*abs(int(r2))*0.01))*0.01*takt,4) 
		m2 = round((abs(int(g2))*abs(int(r2))*0.01)*0.01*takt,4)       
		m3 = round((100-abs(int(g2)))*0.01*takt,4) 
		print(round(m1*100),round(m2*100),round(m3*100))     
    
    
	if 101 > r > 50: #rechts-->linker Motor vorwaerts
		for i in range(0, wiederholungen): 
			if 101 > g >= 50:
				GPIO.output(11, True)
				GPIO.output(8, False)
				GPIO.output(13, True)            
				GPIO.output(16, False)
				GPIO.output(18, True)
				time.sleep(m1) #Geradeaus 

				GPIO.output(11, True)
				GPIO.output(8, False)
				GPIO.output(13, True)            
				GPIO.output(16, False)
				GPIO.output(18, False)
				time.sleep(m2) #Richtung
                
			elif -1 < g < 50:
				GPIO.output(11, True)
				GPIO.output(8, True)
				GPIO.output(13, False)            
				GPIO.output(16, True)
				GPIO.output(18, False)
				time.sleep(m1) #Zurueck 

				GPIO.output(11, True)
				GPIO.output(8, True)
				GPIO.output(13, False)            
				GPIO.output(16, False)
				GPIO.output(18, False)
				time.sleep(m2) #Richtung rueckwaerts
            
			else:
				print("g(erster Wert) ausserhalb der erlaubten Groesse")
                         
			GPIO.output(11, False)
			GPIO.output(8, False)
			GPIO.output(13, False)
			GPIO.output(16, False)
			GPIO.output(18, False)            
			time.sleep(m3) #Leerlauf    
            
	elif -1 < r < 50: #links-->rechter Motor faehrt vorwaerts
		for i in range(0, wiederholungen): 
			if 101 > g >= 50:
				GPIO.output(11, True)
				GPIO.output(8, False)
				GPIO.output(13, True)            
				GPIO.output(16, False)
				GPIO.output(18, True)
				time.sleep(m1) #Geradeaus 
            
				GPIO.output(11, True)
				GPIO.output(8, False)
				GPIO.output(13, False)            
				GPIO.output(16, False)
				GPIO.output(18, True)
				time.sleep(m2) #Richtung

			elif -1 < g < 50:
				GPIO.output(11, True)
				GPIO.output(8, True)
				GPIO.output(13, False)            
				GPIO.output(16, True)
				GPIO.output(18, False)
				time.sleep(m1) #zurueck
            
				GPIO.output(11, True)
				GPIO.output(8, False)
				GPIO.output(13, False)            
				GPIO.output(16, True)
				GPIO.output(18, False)
				time.sleep(m2) #Richtung rueckwaerts
			else:
				print("g(erster Wert) ausserhalb der erlaubten Groesse")  
                
			GPIO.output(11, False)
			GPIO.output(8, False)
			GPIO.output(13, False)
			GPIO.output(16, False)
			GPIO.output(18, False)
            
			time.sleep(m3) #Leerlauf  
            
	elif r == 50: #-->beide Motoren fahren vorwaerts
		for i in range(0, wiederholungen): 
			if 101 > g >= 50:
				GPIO.output(11, True)
				GPIO.output(8, False)
				GPIO.output(13, True)            
				GPIO.output(16, False)
				GPIO.output(18, True)
				time.sleep(m1) #Geradeaus

			elif -1 < g < 50:
				GPIO.output(11, True)
				GPIO.output(8, True)
				GPIO.output(13, False)            
				GPIO.output(16, True)
				GPIO.output(18, False)
				time.sleep(m1) #zurueck
                
			else:
				print("g(erster Wert) ausserhalb der erlaubten Groesse")  
                
			GPIO.output(11, False)
			GPIO.output(8, False)
			GPIO.output(13, False)
			GPIO.output(16, False)
			GPIO.output(18, False)
            
			time.sleep(m3) #Leerlauf 
            
	else:
		print("Unbekannter Befehl")
        
#GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT) #EN
GPIO.output(11, False)
#rechts
GPIO.setup(8, GPIO.OUT) #IN1
GPIO.output(8, False)
GPIO.setup(13, GPIO.OUT) #IN2
GPIO.output(13, False)
#links
GPIO.setup(16, GPIO.OUT) #IN3
GPIO.output(16, False)
GPIO.setup(18, GPIO.OUT) #IN4
GPIO.output(18, False)

        
#Hier gehts los
client = mqtt.Client() 						#Client object
client.on_connect = on_connect 		#Callbacks registrieren 
client.on_message = on_message

client.connect(url, 1883, 60) 				#Connect
client.loop_start()

cmd = input('>')
GPIO.cleanup()

client.loop_stop()