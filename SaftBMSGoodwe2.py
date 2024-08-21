#!/usr/bin/python3
import os
import can
import time
import threading
import logging
from datetime import datetime
import pwd
import grp


#########################################################################
# MM: added for Logging
# FHEM Log-File Format: 2024-07-01_00:01:00 DEVICE DATA
# SAFT_BMM-2024-07.log



# MM: Funktion zur Generierung des dynamischen Dateinamens
def get_dynamic_filename(base_filename):
  current_date = datetime.now()
  return f"{base_filename}-{current_date.year}-{current_date.month:02d}.log"

# MM: Konfiguration des Loggers
logging_filename = get_dynamic_filename("/opt/fhem/log/SAFT_BMM")
logging.basicConfig(
  filename=logging_filename,
  level=logging.INFO,
  format='%(asctime)s SAFT_BMM %(message)s',
  datefmt='%Y-%m-%d_%H:%M:%S'  
)

# Ermitteln der UID und GID des Benutzers 'fhem'
fhem_user = pwd.getpwnam('fhem')
fhem_uid = fhem_user.pw_uid
fhem_gid = grp.getgrnam('dialout').gr_gid

# Ändere die Besitzrechte der Log-Datei
#os.chmod(logging_filename, 0o666)
#os.chown(logging_filename, fhem_uid, fhem_gid)

#########################################################################





os.system('sudo ifconfig can0 down')
os.system('sudo ip link set can0 type can bitrate 250000')
os.system('sudo ifconfig can0 up')

os.system('sudo ifconfig can1 down')
os.system('sudo ip link set can1 type can bitrate 250000')
os.system('sudo ifconfig can1 up')


os.system('sudo cansend can1 000#11.22.33.44')

can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')
#can0.node   .state = 'OPERATIONAL'
can1 = can.interface.Bus(channel = 'can1', bustype = 'socketcan')

# Init
iMax=25 # 25A Dauerlast
i=1
#a = b = c = d = 0
#elementlist1 =bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
elementlist =[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00] 

can_id701 = 0x701  # "0x0701"
can_id181 = 0x181  # "0x0181"
#8h Global battery status
#8h SOC threshold
#8h Battery fault codes n° 1 to 8
#8h Battery fault codes n° 8 to 16
#8h Battery fault codes n° 17 to 24
#8h Battery fault codes n° 25 to 32
#8h Battery fault codes n° 33 to 40
#8h Battery fault codes n° 41 to 48
rawGlobalBatteryStatus = globalBatteryStatus = 0
rawSOCThreshold = sOCThreshold = 0
rawbFC1_8 = 0
rawbFC9_16 = 0
rawbFC17_24 = 0
rawbFC25_32 = 0
rawbFC33_40 = 0
rawbFC41_48 = 0

can_id281 = 0x281  
#10h IMR Continuous
#10h IMR
#10h VMR
#10h PMR
rawIMRContinuous = iMRContinuous = 0
IrawIMR = iMR = 0
rawVMR = vMR = 0
rawPMR = pMR = 0

can_id381 = 0x381  
#10h IMD
#10h VMD
#10h PMD
#8h Battery requests
#Init 0x381
rawIMD = iMD = 0
rawVMD = vMD = 0
rawPMD = pMD = 0
RawBatteryRequests =  batteryRequests = 0

can_id481 = 0x481  
#10h Internal battery Voltage
#10h Internal battery CurrentiMax
#8h Battery System Mode
#8h Battery contactors status
#8h Reserved
#8h SOC
#Init 0x481
rawInternalBatteryVoltage = internalBatteryVoltage = 0
rawInternalBatteryCurrent = internalBatteryCurrent = 0
rawBatterySystemMode = batterySystemMode = 0
rawBatteryContactorsStatus = batteryContactorsStatus = 0
rawReserved = reserved= 0
rawSOC = sOC= 0

can_id420 = 0x420 
canGwIsOnline = 0

# ---------Init Ende ---------


def to_CAN2Byte (el):
    hb = hex(el//256) 
    rest = el-(el//256)*256
    lb = hex(rest)
 
    return (hb)
  
def sendGw():
  threading.Timer(0.150, sendGw).start() # called every ... seconds
  #Sendedaten für Goodwe aufbereiten
  se457 =bytearray(8)

  sOC =71.05
  sOCThreshold = 85.00

  #msgSendGw453 =  can.Message(is_extended_id=False, arbitration_id=0x453, data=[0x44,0x46,0x00,0x00,0x00,0x00,0x00,0x00])
  #  statisch definiert weiter unten

  #msgSendGw455 =  can.Message(is_extended_id=False, arbitration_id=0x455, data=[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
    
  #TODO
  msgSendGw455 =  can.Message(is_extended_id=False, arbitration_id=0x455, data=[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])


  '''Berechnung IMR, IMD nach Grafen	in der Saftdoku		
    IMR                       IMRC
    SOC	    IMR	              SOC	    IMRC
    0-50	  100	              0-85	  100
    51-85	  100-(SOC-50)*1		100
    85-100	65-(SOC-85)*2,67	85-100	100-(SOC-85)*3,35
    100-110	25-(SOC-100)*2,5	100-110	50-(SOC-100)*5
  
  iMR = 0
  if(0<=sOC<51):
    iMR = (100*iMax/100)
  elif(51<=sOC<85):
    iMR = ((100-(sOC-50)*1)*iMax/100)
  elif(85<=sOC<100):
    iMR = ((5-(sOC-85)*2,67)*iMax/100)
  else:
    iMR = ((25-(sOC-100)*2,5)*iMax/100)

  iMD=iMR
  '''
  #msgSendGw456 =  can.Message(is_extended_id=False, arbitration_id=0x456, data=[0xF1,0x0E,0x64,0x00,0xFA,0x00,0x1D,0x0C])
  gwVMR = (int(vMR*10)).to_bytes(2, byteorder='big')
  gwIMR = (int(iMR*10)).to_bytes(2, byteorder='big')
  gwIMD = (int(iMD*10)).to_bytes(2, byteorder='big')
  gwVMD = (int(vMD*10)).to_bytes(2, byteorder='big')
  se456 =bytearray(8)
  se456[0] = gwVMR[1]
  se456[1] = gwVMR[0]
  se456[2] = gwIMR[1]
  se456[3] = gwIMR[0]
  se456[4] = gwIMD[1]
  se456[5] = gwIMD[0]
  se456[6] = gwVMD[1]
  se456[7] = gwVMD[0]
  
  #msgSendGw457 =  can.Message(is_extended_id=False, arbitration_id=0x457, data=elementlist)
  gwSOC = (int(sOC*100)).to_bytes(2, byteorder='big')
  gwSOH = (int(sOC*100)).to_bytes(2, byteorder='big')
  se457 =bytearray(8)
  se457[0] = gwSOC[1]
  se457[1] = gwSOC[0]
  se457[2] = gwSOH[1]
  se457[3] = gwSOH[0]
  se457[4] = 0x00
  se457[5] = 0x00
  se457[6] = 0x00
  se457[7] = 0x00
  
  #msgSendGw458 =  can.Message(is_extended_id=False, arbitration_id=0x458, data=[0x55,0x0E,0x00,0x00,0xc5,0x00,0x00,0x00])
  gwBatteryVoltage = (int(internalBatteryVoltage*10)).to_bytes(2, byteorder='big')
  gwBatteryCurrenet = (int(internalBatteryCurrent*10)).to_bytes(2, byteorder='big',signed=True)
  gwBatteryTemperature = (int(25*10)).to_bytes(2, byteorder='big')
  #TODO temperatur
  se458 =bytearray(8)
  se458[0] = gwBatteryVoltage[1]
  se458[1] = gwBatteryVoltage[0]
  se458[2] = gwBatteryCurrenet[1]
  se458[3] = gwBatteryCurrenet[0]
  se458[4] = gwBatteryTemperature[1]
  se458[5] = gwBatteryTemperature[0]
  se458[6] = 0x00
  se458[7] = 0x00

  #msgSendGw45A =  can.Message(is_extended_id=False, arbitration_id=0x45A, data=[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
  #  statisch definiert weiter unten
  #msgSendGw460 =  can.Message(is_extended_id=False, arbitration_id=0x460, data=[0x00,0x00])
  #  statisch definiert weiter unten
  state =  can1.state
  #print(state)
 # print(state)

  #print('vMR = '+ str(vMR)+'V')
  #print('iMR = '+ str(iMR)+'A')
  #print('iMD = '+ str(iMD)+'A')
  #print('vMD = '+ str(vMD)+'V')
  #print('internalBatteryVoltage = '+ str(internalBatteryVoltage)+'V')
  #print('internalBatteryCurrent = '+ str(internalBatteryCurrent)+'A')
   
  #Can an GW nur senden wenn Online ist sonst läuft Puffer über
  '''
  '''

  #state =  can1.state
 # print(state)

sendGw()   



#neuer Versuch mit mathematischer hex Rechnung
#D*4096+C*256+B*16+A*1
def to_10h (el1, el2):
  return ((el1%16) *1)+((el1//16) *16)+((el2%16) *256)+((el2//16) *4096)


kRemoteSendMsg = can.Message(is_extended_id=False, arbitration_id=0x701, is_remote_frame=True)
k0SendMsg = can.Message(is_extended_id=False, arbitration_id=0x000, data=[1, 0])
#kCloseSendMsg = can.Message(is_extended_id=False, arbitration_id=0x301, data=[0,0,1,0,0,0,0,0])
kCloseSendMsg = can.Message(is_extended_id=False, arbitration_id=0x301, data=[0,0,1])


kCloseSendMsg = can.Message(is_extended_id=False, arbitration_id=0x601, data=[64,88,32,0,0,0,0,0])
kCloseSendMsg = can.Message(is_extended_id=False, arbitration_id=0x601, data=[34,85,32,0,1]) #shell zum Schließen des Schütz: cansend can1 601#2255200001
#kCloseSendMsg = can.Message(is_extended_id=False, arbitration_id=0x601, data=[34,85,32,0,0]) #cansend can1 601#2255200000 wird er wieder geöffnet'
#
# can0.send(kCloseSendMsg)
#print(kCloseSendMsg)
'''
def closeBat():
      #Batterierelais schließen
      threading.Timer(1.0, closeBat).start() # called every ... seconds
      if (batteryContactorsStatus == 0) :
       
        can0.send(kCloseSendMsg)
        print(kCloseSendMsg)
        print ("Relais close")  
closeBat()
'''
'''
#try:
while True:
  #Goodwe daten empfangen
  msgGW = can1.recv()
    
  if (can_id420 == msgGW.arbitration_id and len(msgGW)==8) : 
    canGwIsOnline = 1
  else : 
    print ('nicht decodiert GW')  
    print(msgGW)

except KeyboardInterrupt:
  print('test')
  pass
'''
  
#try:

letzter_log_zeitpunkt = 0

while True:
    



  #Saft BMS empfangen
  msg = can0.recv()
  state =  can0.state
  #print (state)
  #print(msg)

  #Goodwe daten empfangen
  
  #msgGW = can1.recv()
    
    
  # print(state)
  # Batterierelais schließen
  #if (batteryContactorsStatus == 0) :
  #   can0.send(kCloseSendMsg)
  #  print(kCloseSendMsg)
  # print("Relais open")
  
  
  
   #SAFT ist in default Modus und mus zurückgesetzt werden
  if (can_id701 == msg.arbitration_id and len(msg)==1) : #SAFT ist in default Modus und mus zurückgesetzt werden
    can0.send(kRemoteSendMsg)
    can0.send(k0SendMsg)
    #can0.send(kCloseSendMsg)
    #os.system('sudo cansend can0 601#2255200001')
    #print(kCloseSendMsg)
    #print("Relais do open")
  #else :   
    #print("Relais do close")
  
  '''if (rawBatteryContactorsStatus == 0 ) : #SAFT ist in default Modus und mus zurückgesetzt werden
    can0.send(kCloseSendMsg)
    print("Relais do close")'''
  def closeBat():
      #Batterierelais schließen
      threading.Timer(5.0, closeBat).start() # called every ... seconds
      if (batteryContactorsStatus == 0) :
       
        can0.send(kCloseSendMsg)
        print(kCloseSendMsg)
        print ("Relais do close")  
  if (batteryContactorsStatus == 0) :      
    closeBat()
  
  if (can_id181 == msg.arbitration_id and len(msg)==8) :      
    #print ('treffer 0x181')
    #8h Global battery status
    #8h SOC threshold
    #8h Battery fault codes n° 1 to 8
    #8h Battery fault codes n° 8 to 16
    #8h Battery fault codes n° 17 to 24
    #8h Battery fault codes n° 25 to 32
    #8h Battery fault codes n° 33 to 40
    #8h Battery fault codes n° 41 to 48
    i=0      
    for element in msg.data:
      elementlist[i] = element
    i +=1
    rawGlobalBatteryStatus = globalBatteryStatus = elementlist[0]
    rawSOCThreshold = sOCThreshold = elementlist[1]
    rawbFC1_8 = elementlist[2]
    rawbFC9_16 = elementlist[3]
    rawbFC17_24 = elementlist[4]
    rawbFC25_32 = elementlist[5]
    rawbFC33_40 = elementlist[6]
    rawbFC41_48 = elementlist[7]
    print ('id181',' globalBatteryStatus ', globalBatteryStatus,' sOCThreshold ', sOCThreshold ) 
  elif (can_id281 == msg.arbitration_id and len(msg)==8) :
    #print ('treffer 0x281')
    #10h IMR Continuous
    #10h IMR
    #10h VMR
    #10h PMR
    #print(msg) 
    i=0      
    for element in msg.data:
      elementlist[i] = element
      i +=1
    rawIMRContinuous= to_10h (elementlist[0] ,elementlist[1])
    iMRContinuous = rawIMRContinuous  /4 #0,25 A
    rawIMR = to_10h (elementlist[2] ,elementlist[3])
    iMR = rawIMR  /4 #0,25 A
    rawVMR = to_10h (elementlist[4] ,elementlist[5])
    vMR = rawVMR/  40 #25 mV

    rawPMR = to_10h (elementlist[6] ,elementlist[7])
    pMR = rawPMR *10 # 10 W
    print ('id281',' IMRContinuous ', iMRContinuous,' IMR ', iMR,' VMR ', vMR , ' PMR ', pMR  )
  elif (can_id381 == msg.arbitration_id and len(msg)==7) :
    #print ('treffer 0x381')
    #10h IMD
    #10h VMD
    #10h PMD
    #8h Battery requests
    i=0      
    for element in msg.data:
      elementlist[i] = element
      i +=1
    rawIMD = to_10h (elementlist[0] ,elementlist[1])
    iMD = rawIMD  /4 #0,25 A
    rawVMD = to_10h (elementlist[2] ,elementlist[3])
    vMD = rawVMD /  40 #25 mV
    rawPMD = to_10h (elementlist[4] ,elementlist[5])
    pMD = rawPMD *10 # 10 W
    RawBatteryRequests = elementlist[6]
    batteryRequests = RawBatteryRequests
    print ('id381',' IMD ', iMD,' VMD ', vMD , ' PMD ', pMD,' batteryRequests ', batteryRequests )
  elif (can_id481 == msg.arbitration_id and len(msg)==8) : 
    #print ('treffer 0x481')   
    #10h Internal battery Voltage
    #10h Internal battery Current
    #8h Battery System Mode
    #8h Battery contactors status
    #8h Reserved
    #8h SOC    
    i=0     
    #print(msg) 
    for element in msg.data:
      elementlist[i] = element
      i +=1
    #10h Internal battery Voltage
    rawInternalBatteryVoltage = to_10h (elementlist[0] ,elementlist[1])
    internalBatteryVoltage = rawInternalBatteryVoltage / 40 #25 mV
    #10h Internal battery Current
    rawInternalBatteryCurrent = to_10h (elementlist[2] ,elementlist[3])
    if (rawInternalBatteryCurrent <= 32767):
      internalBatteryCurrent = rawInternalBatteryCurrent / 4 #0,25 A
    else:
      internalBatteryCurrent = (rawInternalBatteryCurrent-65535-1) / 4 #0,25 A
    #8h Battery System Mode
    rawBatterySystemMode = elementlist[4]
    batterySystemMode= rawBatterySystemMode
    #8h Battery contactors status
    rawBatteryContactorsStatus = elementlist[5]
    batteryContactorsStatus = rawBatteryContactorsStatus
        
    #8h Reserved
    rawReserved = elementlist[6]
    reserved = rawReserved
    #8h SOC
    rawSOC = elementlist[7]
    sOC = rawSOC  
    
    
    print ('id481 ' ' internalBatteryVoltage ',internalBatteryVoltage, ' internalBatteryCurrent ',internalBatteryCurrent, ' batterySystemMode ', batterySystemMode, ' rawBatteryContactorsStatus ', rawBatteryContactorsStatus, ' reserved ', reserved, ' sOC ',sOC)

    #########################################################################
    # MM: Daten in ein Logile schreiben - alle 5 Min
    aktuelle_zeit = time.time()
  
    # MM: Überprüfe, ob 5 Minuten vergangen sind
    if aktuelle_zeit - letzter_log_zeitpunkt >= 60:  # 300 Sekunden = 5 Minuten
      # Logge die Variablenwerte
      logging.info(f"sOC: {sOC} internalBatteryVoltage: {internalBatteryVoltage} internalBatteryCurrent: {internalBatteryCurrent} batterySystemMode: {batterySystemMode} rawBatteryContactorsStatus: {rawBatteryContactorsStatus} IMD: {iMD} VMD: {vMD} PMD: {pMD} batteryRequests: {batteryRequests} IMRContinuous: {iMRContinuous} IMR: {iMR} VMR: {vMR} PMR: {pMR} globalBatteryStatus: {globalBatteryStatus} sOCThreshold: {sOCThreshold} ")
      letzter_log_zeitpunkt = aktuelle_zeit
    #########################################################################
    # print ('id181',' globalBatteryStatus ', globalBatteryStatus,' sOCThreshold ', sOCThreshold ) 
    # print ('id281',' IMRContinuous ', iMRContinuous,' IMR ', iMR,' VMR ', vMR , ' PMR ', pMR  )
    # print ('id381',' IMD ', iMD,' VMD ', vMD , ' PMD ', pMD,' batteryRequests ', batteryRequests ) 
    # print ('id481',' internalBatteryVoltage ',internalBatteryVoltage, ' internalBatteryCurrent ',internalBatteryCurrent, ' batterySystemMode ', batterySystemMode, ' rawBatteryContactorsStatus ', rawBatteryContactorsStatus, ' reserved ', reserved, ' sOC ',sOC)
   


    
  # elif (can_id420 == msg.arbitration_id and len(msg)==8) : 
  #   canGwIsOnline = 1
  # else : 
    # print ('nicht decodiert SAFT')  
    # print(msg)

  
    


''' 
except KeyboardInterrupt:
  print('ausnahme')
  pass
    '''




"""
#ab hier der senden Teil
can1 = can.interface.Bus(channel = 'can1', bustype = 'socketcan')
msg.id  = 0x453
msg.len = 8
msg.buf[0] = 0x44  # Battery string
msg.buf[1] = 0x46  # Battery string
msg.buf[2] = 0x00
msg.buf[3] = 0x00
msg.buf[4] = 0x00
msg.buf[5] = 0x00
msg.buf[6] = 0x00
msg.buf[7] = 0x00
can1.write(msg) 

msg.id  = 0x455
msg.len = 8
msg.buf[0] = 0x00  # BMS Alarms
msg.buf[1] = 0x00  # BMS Alarms
msg.buf[2] = 0x00
msg.buf[3] = 0x00
msg.buf[4] = 0x00  # BMS Warnings
msg.buf[5] = 0x00  # BMS Warnings
msg.buf[6] = 0x00
msg.buf[7] = 0x00
can1.write(msg) 

msg.id  = 0x456
msg.len = 8
msg.buf[0] = 0xF1  # Charge Voltage
msg.buf[1] = 0x0E  # Charge Voltage
msg.buf[2] = 0x64  # Charge Current
msg.buf[3] = 0x00  # Charge Current
msg.buf[4] = 0xFA  # Max. discharge I
msg.buf[5] = 0x00  # Max. discharge I
msg.buf[6] = 0x1D  # Min. discharge V
msg.buf[7] = 0x0C  # Min. discharge V
can1.write(msg)

msg.id  = 0x457
msg.len = 8
msg.buf[0] = 0xC1  # SOC
msg.buf[1] = 0x1B  # SOC
msg.buf[2] = 0x34  # SOH
msg.buf[3] = 0x21  # SOH
msg.buf[4] = 0x00
msg.buf[5] = 0x00
msg.buf[6] = 0x00
msg.buf[7] = 0x00
can1.write(msg)

msg.id  = 0x458
msg.len = 8
msg.buf[0] = 0x55  # Battery voltage
msg.buf[1] = 0x0E  # Battery voltage
msg.buf[2] = 0x00  # Battery current
msg.buf[3] = 0x00  # Battery current
msg.buf[4] = 0xC5  # Battery temperature
msg.buf[5] = 0x00  # Battery temperature
msg.buf[6] = 0x00
msg.buf[7] = 0x00
can1.write(msg)

msg.id  = 0x45A
msg.len = 8
msg.buf[0] = 0x00
msg.buf[1] = 0x00
msg.buf[2] = 0x00
msg.buf[3] = 0x00
msg.buf[4] = 0x00
msg.buf[5] = 0x00
msg.buf[6] = 0x00
msg.buf[7] = 0x00
can1.write(msg) 

msg.id  = 0x460
msg.len = 2
msg.buf[0] = 0x00
msg.buf[1] = 0x00
msg.buf[2] = 0x00
msg.buf[3] = 0x00
msg.buf[4] = 0x00
msg.buf[5] = 0x00
msg.buf[6] = 0x00
msg.buf[7] = 0x00
can1.write(msg) 


os.system('sudo cansend can1 000#11.22.33.44')

"""
#os.system('sudo ifconfig can0 down')



