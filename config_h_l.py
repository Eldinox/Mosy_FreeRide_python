import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
#Schrittmotor horizontal
Pin1 = 40 # Motor1
Pin2 = 36 # Motor2
Pin3 = 32 # Motor3
Pin4 = 38 # Motor4

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

GPIO.setup(Pin1, GPIO.OUT)
GPIO.setup(Pin2, GPIO.OUT)
GPIO.setup(Pin3, GPIO.OUT)
GPIO.setup(Pin4, GPIO.OUT)

def setStep(w1, w2, w3, w4): #setzt die Pins auf 1 oder 0 je nach Sequenz
    GPIO.output(Pin1, w1)
    GPIO.output(Pin2, w2)
    GPIO.output(Pin3, w3)
    GPIO.output(Pin4, w4)
    
def forward(delay, steps): #laeuft "steps" Anzahl an Schritten alle Sequenzen vorwaerts durch
    for i in range(steps):
        for j in range(StepCount):
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            print (Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)
            
def backwards(delay, steps): #laeuft "steps" Anzahl an Schritten alle Sequenzen rueckwaerts durch
    for i in range(steps):
        for j in reversed(range(StepCount)):
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            print ('back')
            time.sleep(delay)
 
###################################
#hier einstellen
steps_r = 0
steps_l = 5



if steps_r > 0:
	delay = 1 #Verzoegerung zwischen 2 Wiederholungen --> je hoeher desto langsamer dreht er sich   
	steps = 1    #Anzahl der Wiederholungen aller Schritte/Sequenzen
	forward(int(delay) / 1000.0, int(steps_r)) 
	print ('r')    
           
if steps_l > 0 :      
	delay = 1 #Verzoegerung zwischen 2 Wiederholungen --> je hoeher desto langsamer dreht er sich   
	steps = 1    #Anzahl der Wiederholungen aller Schritte/Sequenzen
	backwards(int(delay) / 1000.0, int(steps_l))
	print ('l')    
GPIO.cleanup()