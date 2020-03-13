#!/usr/bin/env python
# -*- coding: cp936 -*-
import sys
import serial
import math
import time
import copy

class YZMotorInterface:
  #CRC 高位字节值表
  __crc_high = [0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80,
	          0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
	          0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00,
	          0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
	          0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80,
	          0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
	          0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00,
	          0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
	          0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81,
	          0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
	          0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
	          0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
	          0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80,
	          0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
	          0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00,
	          0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
	          0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40]
  #CRC 低位字节值表
  __crc_low = [ 0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4, 0x04, 0xCC, 0x0C, 0x0D,
	          0xCD, 0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09, 0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B,
	          0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD, 0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16,
	          0xD6, 0xD2, 0x12, 0x13, 0xD3, 0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6,
	          0xF7, 0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A, 0x3B, 0xFB, 0x39,
	          0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE, 0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C,
	          0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26, 0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61,
	          0xA1, 0x63, 0xA3, 0xA2, 0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF,
	          0x6F, 0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB, 0x7B, 0x7A,
	          0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5, 0x77, 0xB7, 0xB6, 0x76, 0x72,
	          0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91, 0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97,
	          0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C, 0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58,
	          0x98, 0x88, 0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C, 0x44, 0x84,
	          0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80, 0x40 ]

  __kBaudrate = 19200

  def __init__(self,name,port,debug=False):
	  self.name = name
	  self.serial_port = port
	  self.serial = None
	  self.debug_mode = debug
	  self._debug_log('motor interface init: '+self.name)

  def _debug_log(self,msg):
	  if self.debug_mode:
              print('[DEBUG] ['+str(time.time())+']: '+msg)

  def _err_log(self,msg):
	  print('[ERROR] ['+str(time.time())+']: '+msg)

  #open serial port
  def begin(self):
	  try:
	      self.serial = serial.Serial(self.serial_port,self.__kBaudrate,timeout=0.02)
	      self._debug_log('open succeed')
	      return True
	  except Exception,e:
	      self.serial = None
	      self._err_log(repr(e))
	      return False

  #close serial port
  def end(self):
	  try:
	      if self.serial:
                  print "Serial",self.serial
	          self.serial.close()
                  print "Serial",self.serial
	      self.serial = None
	  except Exception,e:
	      self._err_log(repr(e))

  #the number of data that the serial port is waiting to read
  def available(self):
	  if self.serial:
	      return self.serial.inWaiting()
	  else:
	      return 0

  #read data of length l from the serial port
  #l=1: return char
  #l>1: return list
  def read(self,l=1):
	  out = list()
	  rl = None
	  try:
	      rl = self.serial.read(l)
	  except Exception,e:
	      self._err_log("read error")
	      self._err_log(repr(e))
	      return None
	  if rl =='':
	      return None
	  if l==1:
	      return(ord(rl))
	  for r in rl:
	      out.append(ord(r))
	  self._debug_log('read:'+str(out)+str(len(out)))
	  return out

  def write(self,args):
	  args = copy.copy(args)
	  high = self.__calcuCRC(args)>>8
	  low = self.__calcuCRC(args)&0xff
	  args.append(high)
	  args.append(low)
	  self._debug_log('write'+str(args))
	  try:
	      if self.serial!=None:
	          self.serial.write(args)
	      else:
	          self._err_log('self.serial None')
	  except Exception,e:
	      self._err_log(repr(e))

  #get all the information for the motor 'addr'
  #all information length 57
  def getAll(self,addr=1):
    int16 = lambda n: -(~(n-1)&0xffff) if(n>>15) else n
    command = [addr,0x03,0x00,0x00,0x00,0x1a]
    self.read(self.available())
    self.write(command)
    time.sleep(0.05)
    reply = self.read(self.available())
    #print reply
    if self.__check(reply):
      print 'Addr:{:<3}'.format(reply[0]),'         | Modbus Enable:{}'.format(reply[4]),' | Output Enable:{}'.format(int(reply[6]==5))
      print 'Target RPM:{:<5}'.format(int16(reply[7]<<8|reply[8])),' | Real RPM:{:<6.1f}'.format(int16(reply[35]<<8|reply[36])/10.0),
      print ' | Elec Gear:{:>5}/{:<5}'.format(reply[21]<<8|reply[22],reply[23]<<8|reply[24])
      print 'Elec A:{:<5.3f}'.format((reply[33]<<8|reply[34])/2000.0),'     | Elec V:{:<5.3f}'.format((reply[37]<<8|reply[38])/327),
      print '   | 0x19:{:<3}\n'.format(reply[54])
    else:
      reply = None
    return reply

  def isEnable(self,addr=1):
    command = [addr,0x03,0x00,0x01,0x00,0x01]
    t0 = time.time()
    n = self.available()
    self.read(n)
    t1 = time.time()
    self.write(command)
    t2 = time.time()
    data = self.read(7)
    t3 = time.time()
    #print data
    if (data!=None):
    	if(data[0:3]==[addr,3,2]):
    		if self.__check(data):
    			if(data[4]==5):
    			  return True
    			else:
    			  return False
    		else:
    			self._debug_log('check error')
    	else:
    		self._debug_log('False'+str(command)+str(data))
    else:
    	self._debug_log( 'None')
    self._debug_log("{}, {}, {}, {}, {}".format(t0,n,t1,t2,t3))
    #time.sleep(1)
    return False

  #open or colse bus control mode for the motor 'addr'
  def busModeEn(self,en,addr=1):
	  command = [addr,0x06,0x00,0x00,(int(en)&0xffff)>>8,(int(en)&0xffff)&0xff]
	  self.read(self.available())
	  self.write(command)
	  data = self.read(8)
	  if data!=None:
		  if data[0:5]==command[0:5]:
			  return True
		  else:
			  self._err_log('bus mode en/disen fail')
	  else:
		  self._debug_log( 'None')
	  return False

  #set the speed of motor 'addr'
  def setSpeed(self,spe,addr=1,block=True):
	  command = [addr,0x06,0x00,0x02,(int(spe)&0xffff)>>8,(int(spe)&0xffff)&0xff]
	  t0 = time.time()
	  n = self.available()
	  self.read(n)
	  t1 = time.time()
	  self.write(command)
	  t2 = time.time()
	  if block==False:
		  return True
	  data = self.read(8)
	  t3 = time.time()
	  if data!=None:
		  if data[0:5]==command[0:5]:
			  return True
		  else:
			  self._debug_log('False'+str(command)+str(data))
	  else:
		  self._debug_log( 'None')
	  self._debug_log("{}, {}, {}, {}, {}".format(t0,n,t1,t2,t3))
	  #time.sleep(1)
	  return False

  def getPosition(self,addr=1):
    int32 = lambda n: -(~(n-1)&0xffffffff) if(n>>31) else n
    command = [addr,0x03,0x00,0x16,0x00,0x02]
    t0 = time.time()
    n = self.available()
    self.read(n)
    t1 = time.time()
    self.write(command)
    t2 = time.time()
    data = self.read(9)
    t3 = time.time()
    if (data!=None):
      if(data[0:3]==[addr,3,4]):
        if self.__check(data):
	        pp = (data[5]<<8|data[6]) << 16 | (data[3]<<8|data[4])
	        #print pp
	        return int32(pp)
        else:
	        self._debug_log('check error')
      else:
        self._debug_log('False'+str(command)+str(data))
    else:
      self._debug_log( 'None')
    self._debug_log("{}, {}, {}, {}, {}".format(t0,n,t1,t2,t3))
    #time.sleep(1)
    return None

  def __calcuCRC(self,args):
	  u_crc_high = 0xff
	  u_crc_low = 0xff
	  u_index = 0
	  for arg in args:
	      u_index = u_crc_high^arg
	      u_crc_high = u_crc_low^self.__crc_high[u_index]
	      u_crc_low = self.__crc_low[u_index]
	  return(u_crc_high<<8|u_crc_low)

  def __check(self,args):
	  l = len(args)
	  if l<7:
	      return False
	  #print args[l-2]<<8|args[l-1]
	  #print self.__calcuCRC(args[0:l-2])
	  if (args[l-2]<<8|args[l-1]) == self.__calcuCRC(args[0:l-2]):
	      return True
	  else:
	      return False


if __name__ == '__main__':
  motors = YZMotorInterface('motor0','/dev/ttyUSB0',debug = True)
  if motors.begin()==False:
    print 'serial /dev/rs485 open fial'
    exit()
  for addr in range(1,5):
    if motors.busModeEn(1,addr)==False:
      print 'motor '+str(addr)+' busmod enable fail'
      motors.end()
      exit()
    motors.getAll(addr)
  try:
	  #motors.setSpeed(500,addr)
	  spe=0
	  for j in range(10):
		  while spe < 1500:
			  spe=spe+20
			  for addr in range(1,5):
				  result = motors.setSpeed(spe,addr)
				  p = motors.getPosition(addr)
				  time.sleep(0.004)
				  if result==False or p==None:
					  print addr,spe,result,p
		  while spe > 0:
			  spe=spe-20
			  for addr in range(1,5):
				  result = motors.setSpeed(spe,addr)
				  p = motors.getPosition(addr)
				  time.sleep(0.004)
				  if result==False or p==None:
					  print addr,spe,result,p
  finally:
	  for addr in range(1,5):
		  time.sleep(0.02)
		  motors.setSpeed(0,addr)
		  time.sleep(0.02)
		  motors.busModeEn(0,addr)
	  motors.end()
	  print 'test over'








