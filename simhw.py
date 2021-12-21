import subprocess
from gpiozero import Button
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from signal import pause
from subprocess import run
from threading import Lock
import requests
from time import sleep

WIDTH = 128
HEIGHT = 64

# draw text to display
def draw_text(text):
    global oled
    # Clear display.
    oled.fill(0)
    oled.show()
    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new("1", (oled.width, oled.height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    (font_width, font_height) = font.getsize(text)
    # draw text on image
    draw.text(
        (0, 0),
        text,
        font=font,
        fill=255,
    )
    # Display image
    oled.image(image)
    oled.show()

# run correct function on button press
def button_pressed():
    global running, running_mx
    running_mx.acquire()
    if running:
        stop_simulation()
        running = False
    else:
        start_simulation()
        running = True
    running_mx.release()

# start local and remote simulation components
def start_simulation():
    # print message
    draw_text("Starting\nsimulation...")
    # send HTTP request to start remote simulation
    r = requests.get('http://localhost:5000/start')
    # check status code
    if r.status_code == 200:
        # get data
        data = r.json()
        # check return code from server
        if data['code'] != 0:
            draw_text("Error starting\nsimulation!")
        else:
            # launch simulation locally after short delay
            sleep(1)
            run(["sudo", "insmod", "netgpio.ko"])
            draw_text("Simulation\nstarted!")
    else:
        draw_text("HTTP error!")

# stop local and remote simulation components
def stop_simulation():
    # print message
    draw_text("Stopping\nsimulation...")
    # send HTTP request to start remote simulation
    r = requests.get('http://localhost:5000/stop')
    # check status code
    if r.status_code == 200:
        # get data
        data = r.json()
        # check return code from server
        if data['code'] != 0:
            draw_text("Error stopping\nsimulation!")
        else:
            # stop simulation locally after short delay
            sleep(1)
            subprocess.run(["sudo", "rmmod", "netgpio"])
            draw_text("Simulation\nstopped!")
    else:
        draw_text("HTTP error!")

# button to start/stop simulation
button = Button(20)
# whether simulation is running
running = False
running_mx = Lock()
# I2C and OLED screen connection objects
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)

# clear display
oled.fill(0)
oled.show()

# set button press callback
button.when_pressed = button_pressed
# pause main thread
pause()