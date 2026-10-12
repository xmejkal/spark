"""
The button-and-LED firmware (P59's fixture): the LED lights while the button is held.

Written by hand, as a person or the conversation writes it once pins.py exists. The polarity was read from the built
project, not guessed: breadboard.md's wiring (the button's A leg on the BUTTON pin, the other leg on GND, and
STATUS_LED through 330 ohms into the LED's anode, its cathode on GND), and pins.py's BUTTON_PULL = "up": the board's
internal pull-up holds the button high (P204). So the button reads 1 released and 0 pressed, and 1 lights the LED.

update() is the part the Mac exercises. run() calls time.sleep_ms, which only MicroPython has, so it runs on the board.
run() prints `ready` once setup is done, the line a simulated run waits for (P130), then each change of the LED, the lines
a scenario waits on.
"""

import time

from machine import Pin

import pins

BUTTON_PRESSED = 0
LED_ON, LED_OFF = 1, 0
DEFAULT_PERIOD_MS = 20

button = Pin(pins.BUTTON, Pin.IN, Pin.PULL_UP)  # pins.BUTTON_PULL: the board's internal pull-up, no resistor
led = Pin(pins.STATUS_LED, Pin.OUT, value=LED_OFF)


def update():
    """Light the LED while the button is held. Returns True while it is lit."""
    lit = button.value() == BUTTON_PRESSED
    led.value(LED_ON if lit else LED_OFF)
    return lit


def run(period_ms=DEFAULT_PERIOD_MS):
    """The loop main.py starts."""
    print("ready")
    shown = False
    while True:
        lit = update()
        if lit != shown:
            print("LED on" if lit else "LED off")
            shown = lit
        time.sleep_ms(period_ms)
