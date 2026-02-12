import random
import time

def listen_electric_signals(duration=10):
    print('[Electric] Listening for electric signals...')
    for _ in range(duration):
        signal = random.choice([0, 1])
        print(f'[Electric] Signal: {signal}')
        yield signal
        time.sleep(1)

def listen_led_signals(duration=10):
    print('[LED] Listening for LED signals...')
    for _ in range(duration):
        led = random.choice([0, 1])
        print(f'[LED] Signal: {led}')
        yield led
        time.sleep(1)
