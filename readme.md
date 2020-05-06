# Reading the Benewake TFmini LIDAR Module via I2C in Python

The TFmini I2C sensor module is termed a 'LIDAR' module, but really a fast TOF (time of flight) sensor based on a 850nm IR diode. The more common version of the sensor has a serial (UART) interface, but an I2C version exists. The TFmini I2C module can read a distance between 30 cm to 1200 cm at up to 1000hz (standard: 100 Hz). The range and precision depends somewhat on lighting (shorter maximum range in bright sunlight) and reflectivity of the target (shorter maximum range for dark surfaces). 

On a Raspberry Pi, I2c is often the more attractive option communication option, as it allows more sensors to be used in parallel. Unfortunately, as of May 2020, no python library or implementation to read the sensor via python was available online. This repository contains a compact proof of concept that allows reading the sensor values using the smbus2 library in Python, and will hopefully be expanded into a compact library.

The Benewake TFmini product line unfortunately (?) contains several models, with rather different characteristics and communication protocol. The script described here is ONLY intended for the TFmini I2c model (

*## TFmini

Only supports UART/serial

### TFmini I2C

I2c enabled out of the box. **This is the sensor module used here**
[DigiKey](https://www.digikey.com/products/en/sensors-transducers/optical-sensors-distance-measuring/542?k=tfmini&k=&pkeyword=tfmini&sv=0&pv41=356919&sf=0&quantity=&ColumnSort=0&page=1&pageSize=25)
[Robotshop](https://www.robotshop.com/en/benewake-tfmini-micro-lidar-module-i2c-12-m.html)
[Sparkfun(https://www.sparkfun.com/products/14786)

### TFmini-S

Newer version of the TFmini, supports both serial and I2C. Slightly different measurement range, lower power consumption. 

### TFmini plus

Newer version of the TFmini, supports both serial and I2C. Slightly different measurement range, lower power consumption. 

## Hardware setup

The TFmini-I2C module runs on 5V (with a peak current of 80mA!), so make sure the power supply is sufficient. THe SCL and SDA lines run on 3.3V logic level, so can be directly interfaced with a Raspberry Pi. 

Potential concerns: the sensor might use clock stretching, which is broken on Raspberry Pis (supposedly fixed on the Raspberry Pi 4). Reducing the I2C bus speed, or creating a device tree overlay / software I2C bus should fix any problems. 

See here for details:

https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/i2c-clock-stretching
https://github.com/fivdi/i2c-bus/blob/master/doc/raspberry-pi-software-i2c.md

## Software setup

Use raspi-config to enable i2c, reboot.
Install smbus2 via pip3

See here for details:

https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c

