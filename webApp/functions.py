import smbus
import time
import Adafruit_DHT
import io 
import os
import psutil
import sqlite3
import sys
from datetime import datetime
from oled.device import ssd1306, sh1106
from oled.render import canvas
from PIL import ImageDraw, ImageFont
from ctypes import c_short
    



#============================================================================    

dbpath = '/home/pi/sensorProj/final/webApp/sensorlog.db'

#============================================================================    

def i2cA2D(channel):
    """ Read raw analog value from i2c bus 
        based on channel selction 1-4
        returns ints in range 0-255
        returns -1 on error
    """
    address = 0x48

    if channel == 1:
        # soil moisture content
        A0 = 0x40
    elif channel == 2:
        # rain / dev level
        A0 = 0x41
    elif channel == 3:
        # light
        A0 = 0x42
    else:
        # currently spare
        A0 = 0x43
    
    bus = smbus.SMBus(1)

    try:
        bus.write_byte(address,A0)
        # first read sometimes comes back with a 255 so read 5 times, drop first average rest
        values = []
        for i in range(5):
            values.append(bus.read_byte(address))
            time.sleep(0.05)
        #drop the first read
        values.pop(0)
        value = round(sum(values)/len(values))
        return value
    except:
        return (-1)


#============================================================================

def myLight():
    """ Get the light reading value
        and retun as int in range 0-255
        (255 is very bright, 0 is very dark)
        returns -1 on error 
    """
    ret = -1
    try: 
        ret = i2cA2D(3)
        #invert the values to make the graphs more human understandable
        ret = 255 - ret
        return ret
    except:
        return (-999)

#============================================================================        

def mySoil():
    """ Get the soil moisture value
        returns -1 on error 
    """
    ret = -1
    try: 
        ret = i2cA2D(1)
        #invert the values to make the graphs more human understandable
        ret = 255 - ret
        return ret
    except:
        return (-1)

#============================================================================

def myRain():
    """ Get the soil moisture value
        returns -1 on error 
    """
    ret = -1
    try: 
        ret = i2cA2D(2)
        #invert the values to make the graphs more human understandable
        ret = 255 - ret
        return ret
    except:
        return (-1)

#============================================================================

def myHumiTemp():
    """ Get humidity and temperature
        and return them as integers in
        a list
    """
    sensor = Adafruit_DHT.DHT11
    pin = 17
    ret = []
    try: 
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity is not None and temperature is not None:
            ret.append(int(humidity))
            ret.append(int(temperature))
        return ret
    except:
        # drop in some error values so we can filter out at the sql level
        ret = [-999,-999]
        return ret
    
#============================================================================

def myPressureTemp():
    """ Get air pressure[0] and temp[1] 
        from inside the enclosure
        returns list of floats
        (returns -1 on error)

        [ based on the code by Matt Hawkins ]
    
    """
    DEVICE = 0x77 # Default device I2C address
 
    bus = smbus.SMBus(1) # Rev 2 Pi uses 1 
 
    def convertToString(data):
        # Simple function to convert binary data into
        # a string
        return str((data[1] + (256 * data[0])) / 1.2)

    def getShort(data, index):
        # return two bytes from data as a signed 16-bit value
        return c_short((data[index] << 8) + data[index + 1]).value

    def getUshort(data, index):
        # return two bytes from data as an unsigned 16-bit value
        return (data[index] << 8) + data[index + 1]

    def readBmp180(addr=DEVICE):
        # Register Addresses
        REG_CALIB  = 0xAA
        REG_MEAS   = 0xF4
        REG_MSB    = 0xF6
        REG_LSB    = 0xF7
        # Control Register Address
        CRV_TEMP   = 0x2E
        CRV_PRES   = 0x34 
        # Oversample setting
        OVERSAMPLE = 3    # 0 - 3
  
        # Read calibration data
        # Read calibration data from EEPROM
        cal = bus.read_i2c_block_data(addr, REG_CALIB, 22)

        # Convert byte data to word values
        AC1 = getShort(cal, 0)
        AC2 = getShort(cal, 2)
        AC3 = getShort(cal, 4)
        AC4 = getUshort(cal, 6)
        AC5 = getUshort(cal, 8)
        AC6 = getUshort(cal, 10)
        B1  = getShort(cal, 12)
        B2  = getShort(cal, 14)
        MB  = getShort(cal, 16)
        MC  = getShort(cal, 18)
        MD  = getShort(cal, 20)

        # Read temperature
        bus.write_byte_data(addr, REG_MEAS, CRV_TEMP)
        time.sleep(0.005)
        (msb, lsb) = bus.read_i2c_block_data(addr, REG_MSB, 2)
        UT = (msb << 8) + lsb

        # Read pressure
        bus.write_byte_data(addr, REG_MEAS, CRV_PRES + (OVERSAMPLE << 6))
        time.sleep(0.04)
        (msb, lsb, xsb) = bus.read_i2c_block_data(addr, REG_MSB, 3)
        UP = ((msb << 16) + (lsb << 8) + xsb) >> (8 - OVERSAMPLE)

        # Refine temperature
        X1 = ((UT - AC6) * AC5) >> 15
        X2 = (MC << 11) / (X1 + MD)
        B5 = X1 + X2
        temperature = int(B5 + 8) >> 4

        # Refine pressure
        B6  = B5 - 4000
        B62 = int(B6 * B6) >> 12
        X1  = (B2 * B62) >> 11
        X2  = int(AC2 * B6) >> 11
        X3  = X1 + X2
        B3  = (((AC1 * 4 + X3) << OVERSAMPLE) + 2) >> 2

        X1 = int(AC3 * B6) >> 13
        X2 = (B1 * B62) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (AC4 * (X3 + 32768)) >> 15
        B7 = (UP - B3) * (50000 >> OVERSAMPLE)

        P = (B7 * 2) / B4

        X1 = (int(P) >> 8) * (int(P) >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = int(-7357 * P) >> 16
        pressure = int(P + ((X1 + X2 + 3791) >> 4))

        return (round(pressure/100.0),round(temperature/10.0))
    try:
        values = readBmp180()
        return values
    except:
        return (-999)
 
#============================================================================ 
 
def myCpuTemp():
    f = open("/sys/class/thermal/thermal_zone0/temp", "r")
    t = int(f.readline ())
    t = round(t/1000)
    return t
    f.close()
    
#============================================================================
    
def myWebCam():
    
    path = "/home/pi/sensorProj/final/webApp/static/images/cam.jpg"
    commandLine = 'raspistill -n -w 1024 -h 768 -q 80 -t 1 -o ' + path
    os.system(commandLine)
    

#============================================================================

def myLoad():
    """ Get the load average over 
        the last 1, 5, and 15 minutes 
        using os.getloadavg() method
        returns list of three load averages
    """
    load1, load5, load15 = os.getloadavg() 
    
    # return as a list
    ret = (load1,load5,load15)
    return ret
#============================================================================

def myFree():
    s = os.statvfs('/')
    return (int((s.f_bavail * s.f_frsize) / 1024))


#============================================================================

def myTimeStamp():
    """ Get epoch time from os
        Returns epoch time as float
    """
    return int(time.time())
    
#============================================================================

def myUpTime():
    """ Get uptime from os
        Returns uptime in seconds
    """
    return int(time.time() - psutil.boot_time())

#============================================================================

def getLastRow():
    """
        select the last row of sensor data from the datbase
        returns a list
    """
    try:
        with sqlite3.connect(dbpath) as con:
            cur = con.cursor()
            cur.execute("Select * from sensorData where id = (select max(id) from sensorData)")
            data = cur.fetchone()
            return data
            con.close()

    except sqlite3.Error as e:
        print ("failed db read",e)
       
#============================================================================

def dbGetRows(query):
    """
        run query against the datbase
        returns a list
    """
    try:
        with sqlite3.connect(dbpath) as con:   
            cur = con.cursor()  
            cur.execute(query)  
            rows = list(cur.fetchall())  
            return rows
            
    except sqlite3.Error as e:
        print ("failed db read",e)
       

    
#============================================================================


def dbInsertRow():
    """ Get values from all the sensors and insert a row into the databse
        Returns 0 for success other positive int for failure
    """
    myHumidity,myTemp = myHumiTemp()
    myPressure, myCaseTemp = myPressureTemp()
    myLA1,myLA5,myLA15 = myLoad()
    


    commandSQL = "insert into sensorData (id,timestamp,light,rain,soil,pressure,humidity,temperature,encTemp,cpuTemp,loadAv,upTime,memFree) values (null,"
    
    commandSQL += str(myTimeStamp()) + ","
    commandSQL += str(myLight()) + ","
    commandSQL += str(myRain()) + ","
    commandSQL += str(mySoil()) + ","
    commandSQL += str(myPressure) + ","
    commandSQL += str(myHumidity) + ","
    commandSQL += str(myTemp) + ","
    commandSQL += str(myCaseTemp) + ","
    commandSQL += str(myCpuTemp()) + ","
    commandSQL += str(myLA1) + ","
    commandSQL += str(myUpTime()) + ","
    commandSQL += str(myFree()) + ")"
    
    try:
        with sqlite3.connect(dbpath) as con:
            cur = con.cursor()
            cur.execute(commandSQL)
            con.commit()
            con.close()
    except sqlite3.Error as e:
        con.rollback()
        print ("failed db write",e)
    finally:
        con.close()
        
        
#============================================================================

def myOled(data):
    """
        Send information to the on-board OLED display panel
    """
    if not data:
        data ="*"

    def stats(oled):
        font = ImageFont.load_default()
        font2 = ImageFont.truetype('./display/fonts/C&C Red Alert [INET].ttf', 12)
        
        i = 0
        with canvas(oled) as draw:
            for row in data:
                draw.text((0, i), row, font=font2, fill=255)
                i += 11
    
    oled = sh1106(port=1, address=0x3C)
    stats(oled)





#============================================================================

def epochToTime(epoch):
    return str(time.strftime('%H:%M', time.localtime(epoch)))

#============================================================================

def epochToDayTime(epoch):
    return str(time.strftime('%a %H:%M', time.localtime(epoch)))

#============================================================================
def epochToDateTime(epoch):
    return str(time.strftime('%b %d %H:%M', time.localtime(epoch)))

#============================================================================



def lOfTuplesToLoL(listOfTuples):
    """
        SQLite returns a list of tuples 
        tuples are IMMUTABLE!
        so you cannot manipulate the result :(
        
        so you need to convert the tuples to a list of lists
        this function does that :)
    """
    lol = []
    for tup in listOfTuples:
        lol.append(list(tup))
    
    return lol