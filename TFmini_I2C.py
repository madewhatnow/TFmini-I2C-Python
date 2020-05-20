"""

@Author: Wolfgang Schmied

# The MIT License (MIT)
#
# Copyright (c) 2020 Wolfgang Schmied
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""

from smbus2 import SMBus, i2c_msg
import time

__version__ = "0.0.1"


class TFminiI2C:

    """
    Interface to the Benewake TFmini distance (Lidar-like) sensor with I2C interface.
    Usage examples:
        
    Define sensor by giving I2C bus number and sensor address (default: 0x10)
    
    Sensor = TFminiI2C(1, 0x10)
    
    Sensor.read()
    """

    def __init__(self, I2Cbus, address):
        self.I2Cbus = I2Cbus
        self.address = address
        self.RegSetSlave = [0, 38, 1]  # 0x0026, send adddress between 0x10-0x78
        self.RegTriggerMode = [0, 39, 1]  # 0x0027, set trigger mode, default 0x00
        self.RegDefaultSet = [
            0,
            112,
            1,
        ]  # 0x0070, send 0x02 for reset. restore default values, leaves slave address and trigger mode intact
        self.RegDetPattern = [
            0,
            81,
            1,
        ]  # 0x0051, default 0x00, send 0x01 for fixed detection range limits
        self.RegDetRange = [
            0,
            80,
            1,
        ]  # 0x0050, send 0x00 for short (0.3-2m), 0x03 for middle (0.5-5m) or 0x07 for long (1-12m). Set to fixed detection range first.
        self.RegDistUnit = [
            0,
            102,
            1,
        ]  # 0x0066, send 0x00 for mm or 0x01 for cm (default)

    def _setRegister(self, register, setvalue):
        """ helper function """

        self.register = register
        self.setvalue = setvalue
        self.AddReg = i2c_msg.write(self.address, self.register)
        self.SetReg = i2c_msg.write(self.address, [setvalue])

        with SMBus(self.I2Cbus) as bus:
            bus.i2c_rdwr(self.AddReg, self.SetReg)
            time.sleep(0.01)

        return

    def readAll(self):
        """ Return the distance value in selected unit. Default: cm """

        self.write = i2c_msg.write(self.address, [1, 2, 7])
        self.read = i2c_msg.read(self.address, 7)

        with SMBus(self.I2Cbus) as bus:
            bus.i2c_rdwr(self.write, self.read)
            self.data = list(self.read)

            self.TrigFlag = self.data[0]
            self.Dist = self.data[3] << 8 | self.data[2]
            self.Strength = self.data[5] << 8 | self.data[4]
            self.Mode = self.data[6]

        return [self.TrigFlag, self.Dist, self.Strength, self.Mode]

    def readDistance(self):
        """ Return the distance value in selected unit. Default: cm """

        self.write = i2c_msg.write(self.address, [1, 2, 7])
        self.read = i2c_msg.read(self.address, 7)

        with SMBus(self.I2Cbus) as bus:
            bus.i2c_rdwr(self.write, self.read)
            self.data = list(self.read)

            self.Dist = self.data[3] << 8 | self.data[2]

        return self.Dist

    def reset(self):
        """reset sensor"""

        self.reset = i2c_msg.write(self.address, [0x06])

        with SMBus(self.I2Cbus) as bus:
            bus.i2c_rdwr(self.reset)
            time.sleep(0.05)

        return

    def resetdefault(self):

        """ reset sensor to factory settings, leave I2C address as is. """
        self._setRegister(self.RegDefaultSet, 0x02)

    def setAddress(self, newAddress):
        """set new address, needs power cycle to become active - reset apparently not sufficient"""

        self.newAddress = newAddress

        self._setRegister(self.RegSetSlave, self.newAddress)
        print(
            "After power cycle, TFmini "
            + hex(self.address)
            + " will be "
            + hex(self.newAddress)
        )

        return

    def setRange(self, RangeValue):
        """ 
        Use to set a short, medium or long distance range mode.
        Default behaviour is automatic switching, with a loss in accuracy while changing. 
        For some applications, fixed range mode might be more useful. 
        Here, first automatic changes are disabled, then a specific range is locked in.
        Use 0x00, 0x03 or 0x07 for short, medium or long range.
        """

        self.RangeValue = RangeValue

        while RangeValue not in {0x00, 0x03, 0x07}:
            print("Use 0x00, 0x03 or 0x07 for short, medium or long range.")
            return

        self.AddReg = i2c_msg.write(self.address, self.RegDetPattern)
        self._setReg = i2c_msg.write(self.address, [0x01])
        """deactivate automatic range switching"""

        print("Set range mode to fixed.")
        with SMBus(self.I2Cbus) as bus:
            bus.i2c_rdwr(self.AddReg, self.SetReg)

        print("Set range distance.")
        self.AddReg2 = i2c_msg.write(self.address, self.RegDetRange)
        self.SetReg2 = i2c_msg.write(self.address, [self.RangeValue])
        """ set fixed range """

        with SMBus(self.I2Cbus) as bus:
            bus.i2c_rdwr(self.AddReg2, self.SetReg2)
            time.sleep(0.01)

        return

    def setUnit(self, RangeUnit):

        self.RangeUnit = RangeUnit

        while self.RangeUnit not in {0x00, 0x01}:
            print("Use 0x00 for mm, or 0x01 for cm.")
            return

        self._setRegister(self.RegDistUnit, self.RangeUnit)
        return


"""
Example usage:
                  
Sensor0 = TFminiI2C(1, 0x10)
Sensor1 = TFminiI2C(1, 0x11)
Sensor2 = TFminiI2C(1, 0x12)

print(Sensor0.readDistance())
print(Sensor1.readAll())
print(Sensor2.readAll())

Sensor0.setUnit(0x00) #for mm
Sensor1.setUnit(0x01) #for cm

Sensor2.setRange(0x05)

"""
