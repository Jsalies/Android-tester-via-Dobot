import os
import select
import signal
import stat
import struct
import sys
import time
import serial
import threading
import serial.tools.list_ports

class Monsoon:

  def __init__(self, device):
    """Ouvre le device positionné au port passer en argument"""
    self._coarse_ref = self._fine_ref = self._coarse_zero = self._fine_zero = 0
    self._coarse_scale = self._fine_scale = 0
    self._last_seq = 0
    self.start_voltage = 0
    self.ser = serial.Serial(device, timeout=1)

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
        out = []
        for main, usb, aux, voltage in data:
          if main & 1:
            out.append(((main & ~1) - self._coarse_zero) * self._coarse_scale)
          else:
            out.append((main - self._fine_zero) * self._fine_scale)
        return out
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