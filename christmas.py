from datetime import datetime
from threading import Timer

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

import uvicorn

from gpiozero import LEDBoard
from gpiozero.tools import random_values
from signal import pause

# Tree control

LED_ORDER = [4,15,13,21,25,8,5,10,16,17,27,26,24,9,12,6,20,19,14,18,11,7,23,22,2]

tree = LEDBoard(*LED_ORDER,
                pwm=True)
delay_value = 0.4
intensity_coef = 0.8

def party_mode():
    def intensity(coef):
        value_gen = random_values()
        while value_gen:
            yield next(value_gen) * coef

    for led in tree:
        if led.pin.number == 2:
            # star led
            led.pulse(2, 2)
            led.source = None
            continue
        led.source_delay = delay_value
        led.source = intensity(intensity_coef)


def calendar_mode():
    def turn_on_if_day(pin_day):
        while True:
            today = datetime.today()
            current_day = today.day
            if current_day >= pin_day:
                yield intensity_coef
            else:
                yield 0

    for day, led in enumerate(tree.leds):
        led.source_delay = delay_value
        led.source = turn_on_if_day(day + 1)


def is_it_christmas_yet():
    today = datetime.today()
    return (today.day == 25
            and today.hour == 00
            and today.minute == 00)


def check_for_christmas_party():
    if is_it_christmas_yet():
        current_mode = -1
        modes[current_mode]()
    else:
        christimer = Timer(1, check_for_christmas_party)
        christimer.start()


modes = [calendar_mode, party_mode]
current_mode = 0

check_for_christmas_party()

# REST API

app = FastAPI()

@app.get("/api/on")
def on():
    modes[current_mode]()

@app.get("/api/off")
def off():
    for led in tree:
        led.source = None
        led.off()

@app.get("/api/switch")
def switch_mode():
    global current_mode
    current_mode += 1
    current_mode %= len(modes)
    on()

@app.get("/api/intensity")
def get_intensity() -> float:
    return intensity_coef

class Intensity(BaseModel):
    value: float

@app.put("/api/intensity", status_code=204)
def set_intensity(intensity: Intensity) -> None:
    global intensity_coef
    intensity_coef = intensity.value
    intensity_coef = min(intensity_coef, 1.0)
    intensity_coef = max(intensity_coef, 0.0)
    on()

@app.get("/api/delay")
def get_delay() -> float:
    return delay_value

class Delay(BaseModel):
    value: float

@app.put("/api/delay", status_code=204)
def set_intensity(delay: Delay) -> None:
    global delay_value
    delay_value = delay.value
    delay_value = min(delay_value, 2.0)
    delay_value = max(delay_value, 0.0)
    on()

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == '__main__':
    on()
    uvicorn.run(app, host='0.0.0.0', port=9876)
