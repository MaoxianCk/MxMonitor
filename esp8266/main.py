# main.py
print('do main.py!')
import utime
import network
import utime
import urequests
from machine import Pin
import sys
from machine import Pin, I2C
import ssd1306
import micropython

SSID = "ASUS-MX"
PASSWORD = "cst05180"
wlan = None
display = None


def do_connect():
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        now = utime.time()
        # 每15s 重连
        if utime.time() - now > 15:
            print("connect timeout!")
            break

    if wlan.isconnected():
        twinkleLED()
        print('network config:', wlan.ifconfig())


def twinkleLED(onTime=0.1, offTime=0.1, times=3, lastStatus=False):
    p0 = Pin(2, Pin.OUT)
    p0.off()
    if lastStatus == None:
        lastStatus = p0.value()
    for i in range(0, times):
        p0.on()
        utime.sleep(onTime)
        p0.off()
        utime.sleep(offTime)
    p0.value(lastStatus)


def getData():
    try:
        res = urequests.get('http://192.168.2.2:7777/info')
    except OSError as e:
        print('request server fail. msg: {}'.format(e))
        return None
    # print(res.json())
    return res.json()


def connectSC():
    i2c = I2C(scl=Pin(5), sda=Pin(4))
    global display
    display = ssd1306.SSD1306_I2C(128, 64, i2c)


def displaySC(data):
    if display != None:
        if data is not None:
            display.fill(0)
            display.text('cpu: {}'.format(data['cpu']['usageSumPercentStr']), 0, 0)
            display.show()
        else:
            print('data is None')
    else:
        print('display is None')


if __name__ == '__main__':
    try:
        do_connect()
        connectSC()
        while wlan.isconnected():
            data = getData()
            displaySC(data)
            micropython.mem_info()
            utime.sleep(5)

    except Exception as e:
        print('init error: ')
        sys.print_exception(e)

    finally:
        print('init done')