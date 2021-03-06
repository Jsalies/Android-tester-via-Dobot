#!/usr/bin/python
# Copyright (C) 2014 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Interface for a USB-connected Monsoon power meter
(http://msoon.com/LabEquipment/PowerMonitor/).
This file requires gflags, which requires setuptools.
To install setuptools: sudo apt-get install python-setuptools
To install gflags, see http://code.google.com/p/python-gflags/
To install pyserial, see http://pyserial.sourceforge.net/
Example usages:
  Set the voltage of the device 7536 to 4.0V
  python monsoon.py --voltage=4.0 --serialno 7536
  Get 5000hz data from device number 7536, with unlimited number of samples
  python monsoon.py --samples -1 --hz 5000 --serialno 7536
  Get 200Hz data for 5 seconds (1000 events) from default device
  python monsoon.py --samples 100 --hz 200
  Get unlimited 200Hz data from device attached at /dev/ttyACM0
  python monsoon.py --samples -1 --hz 200 --device /dev/ttyACM0
Output columns for collection with --samples, separated by space:
  TIMESTAMP OUTPUT OUTPUT_AVG USB USB_AVG
   |                |          |   |
   |                |          |   ` (if --includeusb and --avg)
   |                |          ` (if --includeusb)
   |                ` (if --avg)
   ` (if --timestamp)
"""
import fcntl
import os
import select
import signal
import stat
import struct
import sys
import time
import collections
import serial           # http://pyserial.sourceforge.net/
import threading
continuer=1

class Monsoon:
  """
  Provides a simple class to use the power meter, e.g.
  mon = monsoon.Monsoon()
  mon.SetVoltage(3.7)
  mon.StartDataCollection()
  mydata = []
  while len(mydata) < 1000:
    mydata.extend(mon.CollectData())
  mon.StopDataCollection()
  """
  def __init__(self, device=None, serialno=None, wait=1):
    """
    Establish a connection to a Monsoon.
    By default, opens the first available port, waiting if none are ready.
    A particular port can be specified with "device", or a particular Monsoon
    can be specified with "serialno" (using the number printed on its back).
    With wait=0, IOError is thrown if a device is not immediately available.
    """
    self._coarse_ref = self._fine_ref = self._coarse_zero = self._fine_zero = 0
    self._coarse_scale = self._fine_scale = 0
    self._last_seq = 0
    self.start_voltage = 0
    if device:
      self.ser = serial.Serial(device, timeout=1)
      return
    while True:  # try all /dev/ttyACM* until we find one we can use
      for dev in os.listdir("/dev"):
        if not dev.startswith("ttyACM"): continue
        tmpname = "/tmp/monsoon.%s.%s" % (os.uname()[0], dev)
        self._tempfile = open(tmpname, "w")
        try:
          os.chmod(tmpname, 0666)
        except OSError:
          pass
        try:  # use a lockfile to ensure exclusive access
          fcntl.lockf(self._tempfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError as e:
          print >>sys.stderr, "device %s is in use" % dev
          continue
        try:  # try to open the device
          self.ser = serial.Serial("/dev/%s" % dev, timeout=1)
          self.StopDataCollection()  # just in case
          self._FlushInput()  # discard stale input
          status = self.GetStatus()
        except Exception as e:
          print >>sys.stderr, "error opening device %s: %s" % (dev, e)
          continue
        if not status:
          print >>sys.stderr, "no response from device %s" % dev
        elif serialno and status["serialNumber"] != serialno:
          print >>sys.stderr, ("Note: another device serial #%d seen on %s" %
                               (status["serialNumber"], dev))
        else:
          self.start_voltage = status["voltage1"]
          return
      self._tempfile = None
      if not wait: raise IOError("No device found")
      print >>sys.stderr, "waiting for device..."
      time.sleep(1)
  def GetStatus(self):
    """ Requests and waits for status.  Returns status dictionary. """
    # status packet format
    STATUS_FORMAT = ">BBBhhhHhhhHBBBxBbHBHHHHBbbHHBBBbbbbbbbbbBH"
    STATUS_FIELDS = [
        "packetType", "firmwareVersion", "protocolVersion",
        "mainFineCurrent", "usbFineCurrent", "auxFineCurrent", "voltage1",
        "mainCoarseCurrent", "usbCoarseCurrent", "auxCoarseCurrent", "voltage2",
        "outputVoltageSetting", "temperature", "status", "leds",
        "mainFineResistor", "serialNumber", "sampleRate",
        "dacCalLow", "dacCalHigh",
        "powerUpCurrentLimit", "runTimeCurrentLimit", "powerUpTime",
        "usbFineResistor", "auxFineResistor",
        "initialUsbVoltage", "initialAuxVoltage",
        "hardwareRevision", "temperatureLimit", "usbPassthroughMode",
        "mainCoarseResistor", "usbCoarseResistor", "auxCoarseResistor",
        "defMainFineResistor", "defUsbFineResistor", "defAuxFineResistor",
        "defMainCoarseResistor", "defUsbCoarseResistor", "defAuxCoarseResistor",
        "eventCode", "eventData", ]
    self._SendStruct("BBB", 0x01, 0x00, 0x00)
    while True:  # Keep reading, discarding non-status packets
      bytes = self._ReadPacket()
      if not bytes: return None
      if len(bytes) != struct.calcsize(STATUS_FORMAT) or bytes[0] != "\x10":
        print >>sys.stderr, "wanted status, dropped type=0x%02x, len=%d" % (
                ord(bytes[0]), len(bytes))
        continue
      status = dict(zip(STATUS_FIELDS, struct.unpack(STATUS_FORMAT, bytes)))
      assert status["packetType"] == 0x10
      for k in status.keys():
        if k.endswith("VoltageSetting"):
          status[k] = 2.0 + status[k] * 0.01
        elif k.endswith("FineCurrent"):
          pass # needs calibration data
        elif k.endswith("CoarseCurrent"):
          pass # needs calibration data
        elif k.startswith("voltage") or k.endswith("Voltage"):
          status[k] = status[k] * 0.000125
        elif k.endswith("Resistor"):
          status[k] = 0.05 + status[k] * 0.0001
          if k.startswith("aux") or k.startswith("defAux"): status[k] += 0.05
        elif k.endswith("CurrentLimit"):
          status[k] = 8 * (1023 - status[k]) / 1023.0
      return status
  def RampVoltage(self, start, end):
    v = start
    if v < 3.0: v = 3.0       # protocol doesn't support lower than this
    while (v < end):
      self.SetVoltage(v)
      v += .1
      time.sleep(.1)
    self.SetVoltage(end)
  def SetVoltage(self, v):
    """ Set the output voltage, 0 to disable. """
    if v == 0:
      self._SendStruct("BBB", 0x01, 0x01, 0x00)
    else:
      self._SendStruct("BBB", 0x01, 0x01, int((v - 2.0) * 100))
  def SetMaxCurrent(self, i):
    """Set the max output current."""
    assert i >= 0 and i <= 8
    val = 1023 - int((i/8)*1023)
    self._SendStruct("BBB", 0x01, 0x0a, val & 0xff)
    self._SendStruct("BBB", 0x01, 0x0b, val >> 8)
  def SetUsbPassthrough(self, val):
    """ Set the USB passthrough mode: 0 = off, 1 = on,  2 = auto. """
    self._SendStruct("BBB", 0x01, 0x10, val)
  def StartDataCollection(self):
    """ Tell the device to start collecting and sending measurement data. """
    self._SendStruct("BBB", 0x01, 0x1b, 0x01) # Mystery command
    self._SendStruct("BBBBBBB", 0x02, 0xff, 0xff, 0xff, 0xff, 0x03, 0xe8)
  def StopDataCollection(self):
    """ Tell the device to stop collecting measurement data. """
    self._SendStruct("BB", 0x03, 0x00) # stop
  def CollectData(self):
    """ Return some current samples.  Call StartDataCollection() first. """
    while True:  # loop until we get data or a timeout
      bytes = self._ReadPacket()
      if not bytes: return None
      if len(bytes) < 4 + 8 + 1 or bytes[0] < "\x20" or bytes[0] > "\x2F":
        print >>sys.stderr, "wanted data, dropped type=0x%02x, len=%d" % (
            ord(bytes[0]), len(bytes))
        continue
      seq, type, x, y = struct.unpack("BBBB", bytes[:4])
      data = [struct.unpack(">hhhh", bytes[x:x+8])
              for x in range(4, len(bytes) - 8, 8)]
      if self._last_seq and seq & 0xF != (self._last_seq + 1) & 0xF:
        print >>sys.stderr, "data sequence skipped, lost packet?"
      self._last_seq = seq
      if type == 0:
        if not self._coarse_scale or not self._fine_scale:
          print >>sys.stderr, "waiting for calibration, dropped data packet"
          continue
        def scale(val):
          if val & 1:
            return ((val & ~1) - self._coarse_zero) * self._coarse_scale
          else:
            return (val - self._fine_zero) * self._fine_scale
        out_main = []
        out_usb = []
        for main, usb, aux, voltage in data:
          out_main.append(scale(main))
          out_usb.append(scale(usb))
        return (out_main, out_usb)
      elif type == 1:
        self._fine_zero = data[0][0]
        self._coarse_zero = data[1][0]
        # print >>sys.stderr, "zero calibration: fine 0x%04x, coarse 0x%04x" % (
        #     self._fine_zero, self._coarse_zero)
      elif type == 2:
        self._fine_ref = data[0][0]
        self._coarse_ref = data[1][0]
        # print >>sys.stderr, "ref calibration: fine 0x%04x, coarse 0x%04x" % (
        #     self._fine_ref, self._coarse_ref)
      else:
        print >>sys.stderr, "discarding data packet type=0x%02x" % type
        continue
      if self._coarse_ref != self._coarse_zero:
        self._coarse_scale = 2.88 / (self._coarse_ref - self._coarse_zero)
      if self._fine_ref != self._fine_zero:
        self._fine_scale = 0.0332 / (self._fine_ref - self._fine_zero)
  def _SendStruct(self, fmt, *args):
    """ Pack a struct (without length or checksum) and send it. """
    data = struct.pack(fmt, *args)
    data_len = len(data) + 1
    checksum = (data_len + sum(struct.unpack("B" * len(data), data))) % 256
    out = struct.pack("B", data_len) + data + struct.pack("B", checksum)
    self.ser.write(out)
  def _ReadPacket(self):
    """ Read a single data record as a string (without length or checksum). """
    len_char = self.ser.read(1)
    if not len_char:
      print >>sys.stderr, "timeout reading from serial port"
      return None
    data_len = struct.unpack("B", len_char)
    data_len = ord(len_char)
    if not data_len: return ""
    result = self.ser.read(data_len)
    if len(result) != data_len: return None
    body = result[:-1]
    checksum = (data_len + sum(struct.unpack("B" * len(body), body))) % 256
    if result[-1] != struct.pack("B", checksum):
      print >>sys.stderr, "invalid checksum from serial port"
      return None
    return result[:-1]
  def _FlushInput(self):
    """ Flush all read data until no more available. """
    self.ser.flush()
    flushed = 0
    while True:
      ready_r, ready_w, ready_x = select.select([self.ser], [], [self.ser], 0)
      if len(ready_x) > 0:
        print >>sys.stderr, "exception from serial port"
        return None
      elif len(ready_r) > 0:
        flushed += 1
        self.ser.read(1)  # This may cause underlying buffering.
        self.ser.flush()  # Flush the underlying buffer too.
      else:
        break
    if flushed > 0:
      print >>sys.stderr, "dropped >%d bytes" % flushed

  def start(self,file):
    lancermesure=threading.Thread(target=self.getsamples,args=[file])
    lancermesure.start()

  def getsamples(self,file):
    print ("start")
    global continuer
    """ Simple command-line interface for Monsoon."""
    num_channels = 2
    #num_channels = 1
    self.SetVoltage(4.5)
    self.SetMaxCurrent(3.)
    items = sorted(self.GetStatus().items())
    self.SetUsbPassthrough(1)

    # Make sure state is normal
    self.StopDataCollection()
    status = self.GetStatus()
    native_hz = status["sampleRate"] * 1000
    # Collect and average samples as specified
    self.StartDataCollection()
    self.CollectData()
    # In case FLAGS.hz doesn't divide native_hz exactly, use this invariant:
    # 'offset' = (consumed samples) * FLAGS.hz - (emitted samples) * native_hz
    # This is the error accumulator in a variation of Bresenham's algorithm.
    emitted = offset = 0
    chan_buffers = tuple([] for _ in range(num_channels))
    # past n samples for rolling average
    history_deques = tuple(collections.deque() for _ in range(num_channels))
    try:
        fichier=open(file,"w")
        fichier.write("!!!ligne inutile!!!\n")
        fichier.write("Time,Power\n")
        last_flush = time.time()
        deb=time.time()
        continuer=1
        while continuer==1:
          # The number of raw samples to consume before emitting the next output
          need = (native_hz - offset + 5000 - 1) / 5000
          if need > len(chan_buffers[0]):     # still need more input samples
            chans_samples = self.CollectData()
            if not all(chans_samples): break
            for chan_buffer, chan_samples in zip(chan_buffers, chans_samples):
              chan_buffer.extend(chan_samples)
          else:
            # Have enough data, generate output samples.
            # Adjust for consuming 'need' input samples.
            offset += need * 5000
            while offset >= native_hz:  # maybe multiple, if FLAGS.hz > native_hz
              this_sample = [sum(chan[:need]) / need for chan in chan_buffers]
              fichier.write(str(round(10**6*(time.time()-deb),1))+",")
              data_to_print = this_sample
              fmt = ' '.join('%f' for _ in data_to_print)
              fichier.write(str(round(data_to_print[0]*4.5,4))+"\n")
              sys.stdout.flush()
              offset -= native_hz
              emitted += 1              # adjust for emitting 1 output sample
            chan_buffers = tuple(c[need:] for c in chan_buffers)
            now = time.time()
            if now - last_flush >= 0.99:  # flush every second
              sys.stdout.flush()
              last_flush = now
        fichier.close()
    except KeyboardInterrupt:
        print >>sys.stderr, "interrupted"
    self.StopDataCollection()

  def stop(self,value,temp1,freq1,temp2,freq2):
      global continuer
      print ("stop")
      continuer=0

if __name__ == '__main__':
  # Define flags here to avoid conflicts with people who use us as a library
  mon=Monsoon()
  print("debut")
  lancermesure=threading.Thread(target=mon.start,args=["bob.csv"])
  lancermesure.start()
  print("here")
  time.sleep(25)
  mon.stop(True,0,0,0,0)
  os.remove("bob.csv")
