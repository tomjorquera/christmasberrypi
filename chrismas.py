from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

import uvicorn

from gpiozero import LEDBoard
from gpiozero.tools import random_values
from signal import pause

# Tree control

tree = LEDBoard(*range(2,28),pwm=True)
delay_value = 0.4
intensity_coef = 0.8


def intensity(coef):
    value_gen = random_values()
    while value_gen:
        yield next(value_gen) * coef

def on():
    for led in tree:
        if led.pin.number == 2:
            # star led
            led.pulse(2, 2)
            continue
        led.source_delay = delay_value
        led.source = intensity(intensity_coef)

def off():
    for led in tree:
        led.source = None
        led.off()


# REST API

app = FastAPI()

@app.get("/api/on")
def get_on() -> None:
    on()

@app.get("/api/off")
def get_off() -> None:
    off()

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
