from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import uvicorn

from gpiozero import LEDBoard
from gpiozero.tools import random_values
from signal import pause


# Tree control

tree = LEDBoard(*range(2,28),pwm=True)

def intensity(coef=0.8):
    value_gen = random_values()
    while value_gen:
        yield next(value_gen) * coef

def on():
    for led in tree:
        if led.pin.number == 2:
            # star led
            led.pulse(2, 2)
            continue
        led.source_delay = 0.4
        led.source = intensity()

def off():
    for led in tree:
        led.source = None
        led.off()


# REST API



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/on")
def get_on():
    on()

@app.get("/api/off")
def get_off():
    off()

if __name__ == '__main__':
    on()
    uvicorn.run(app, host='0.0.0.0', port=9876)
