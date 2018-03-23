#!/usr/bin/env python3
import itertools
import colorsys
import neopixel
import time
import primefac
import math
from math import sin, cos, pi
import random


black = neopixel.Color(0, 0, 0)
red = neopixel.Color(255, 0, 0)
blue = neopixel.Color(0, 255, 0)
green = neopixel.Color(0, 0, 255)


def rgb_to_irgb(rgb):
    '''RGB to int RGB'''
    r, g, b = rgb
    return neopixel.Color(int(r * 255), int(g * 255), int(b * 255))


def color_wheel(hue):
    '''hue on a scale from 0 to 1'''
    return rgb_to_irgb(colorsys.hsv_to_rgb(hue, 1, 1))


def mapp(val, inmin, inmax, outmin, outmax):
    '''maps val on a scale from inmin to inmax to a value on a scale from outmin to outmax'''
    return (val - inmin) / (inmax - inmin) * (outmax - outmin) + outmin


def color_val(val):
    '''visualizes value val in a scale -1 1 on a scale between red and blue'''
    n = 3
    rgb = (
        val**n    if val > 0 else 0,
        0,
        (-val)**n if val < 0 else 0,
    )
    return rgb_to_irgb(rgb)


def animate_primes(strip, max_prime=1000, **kwargs):
    max_prime = 1000    
    sequence = primefac._primefac.primes(max_prime)
    animate_sequence(strip, sequence, **kwargs )

def animate_sequence(strip, sequence, n_colors=200, delay=0.02, n_set_before_off=25):
    pixel_times_set = {i: 0 for i in range(strip.numPixels())}
    while True:
        for i, elem in enumerate(sequence):
            print(elem)
            pixel = elem % strip.numPixels()
            pixel_times_set[pixel] = i
            hue = (elem % n_colors) / n_colors
            color = rgb_to_irgb(colorsys.hsv_to_rgb(hue, 1, 1))
            strip.setPixelColor(pixel, color)

            for pixel in range(strip.numPixels()):
                if pixel_times_set[pixel] + n_set_before_off < i:
                    strip.setPixelColor(pixel, black)

            strip.show()
            time.sleep(delay)


def to_binary(n, size):
    '''return an integer in binary as a string'''
    return '{n:0{size}b}'.format(**locals())


def animate_timestamp(strip, delay=0.0001):
    '''Display the number of miliseconds since Jan 1, 1970' as a binary number

    (AKA binary counter)'''
    while True:
        timestamp = int(time.time() * 1000)
        for pixel, digit in enumerate(to_binary(timestamp, strip.numPixels())):
            color = color_wheel(pixel / strip.numPixels()) if digit == '1' else black
            strip.setPixelColor(pixel, color)
        print(timestamp, to_binary(timestamp, strip.numPixels()))
        strip.show()
        time.sleep(delay)


def animate_factorial(strip):
    '''Display n! in binary'''
    delay = 0.5
    acc = 2
    while True:
        for i in itertools.count(2):
            acc *= i
            for pixel, digit in enumerate(to_binary(acc, strip.numPixels())):
                color = color_wheel(pixel / strip.numPixels()) if digit == '1' else black
                strip.setPixelColor(pixel, color)
            print(i, acc, to_binary(acc, strip.numPixels()))
            strip.show()
            time.sleep(delay)


def reflect(pos, size, onbounce=None):
    if pos >= size:
        if onbounce: onbounce()
        return size - (pos - size + 1)
    elif pos < 0:
        if onbounce: onbounce()
        return -pos
    else:
        return pos


def draw_wave(pixel_buffer, wave_spec):
    for pixel in range(round(wave_spec['pos']), round(wave_spec['pos'] + wave_spec['wavelength'])):
        val = sin((pixel - wave_spec['pos']) * 2 * math.pi / wave_spec['wavelength']) * wave_spec['amp']
        pixel_buffer[reflect(pixel, len(pixel_buffer))] += val


def draw_buffer(strip, pixel_buffer):
    for pixel, val in enumerate(pixel_buffer):
        color = color_val(val)
        strip.setPixelColor(pixel, color)


def animate_waves(strip, wave_specs=None):
    if wave_specs is None:
        wave_specs = [
            {'pos': 30, 'velocity': 10, 'wavelength': 6, 'amp': 1},
            {'pos': 10, 'velocity': -30, 'wavelength': 7, 'amp': 1},
            {'pos': 20, 'velocity': 20, 'wavelength': 5, 'amp': 1},
            # {'pos': 20, 'velocity': 50, 'wavelength': 5, 'amp': 1},
        ]
    delay = 0.001

    while True:
        pixel_buffer = [0] * strip.numPixels()
        print('frame')
        for wave_spec in wave_specs:
            draw_wave(pixel_buffer, wave_spec)
            bounced = []
            #print(wave_spec['pos'], wave_spec['velocity'], wave_spec['wavelength'])
            wave_spec['pos'] = reflect(wave_spec['pos'] + wave_spec['velocity'] * delay,
                                       len(pixel_buffer),
                                       lambda: bounced.append('hello world'))
            if bounced:
                print('bounce')
                wave_spec['velocity'] = -wave_spec['velocity']

        draw_buffer(strip, pixel_buffer)
        strip.show()
        time.sleep(delay)


def animate_icicle(strip, prob_water=0.001, drip_speed=20, max_splash_height=5, splash_speed=4, delay=0.0001):
    # note that speed is really 'inverse speed', number of frames between things
    ice_color   = neopixel.Color(200, 200, 255)
    water_color = neopixel.Color(40, 40, 255)
    drip_falling = False
    drip_pos = 0
    splash_rising = False
    splash_pos = 0
    splishes = []
    splash_height = 0
    icicle_length = random.randint(14, 17)
    drip_speed_ = drip_speed

    for frame in itertools.count():
        for i in range(icicle_length):
            strip.setPixelColor(strip.numPixels() - i - 1, ice_color)

        if drip_falling:
            strip.setPixelColor(drip_pos, water_color)

        if splash_rising:
            strip.setPixelColor(splash_pos, water_color)
            for splish in splishes:
                strip.setPixelColor(splish, water_color)

        if drip_falling and frame % round(drip_speed_) == 0:
            if drip_pos == 0:
                print('splash')
                drip_falling = False
                splash_rising = True
                splash_pos = 0
                splash_height = random.randint(0, max_splash_height)
            else:
                strip.setPixelColor(drip_pos, black)
                drip_pos -= 1
                drip_speed_ -= 0.4

        if splash_rising and frame % splash_speed == 0:
            if splash_pos > splash_height:
                strip.setPixelColor(splash_pos, black)
                for splish in splishes:
                    strip.setPixelColor(splish, black)
                splash_rising = False
            else:
                strip.setPixelColor(splash_pos, black)
                for i in range(0, splash_pos):
                    if random.random() < 0.01:
                        splishes.append(splash_pos)
                splash_pos += 1

        if random.random() < prob_water and not drip_falling:
            print('drip')
            drip_pos = strip.numPixels() - icicle_length - 1
            drip_speed_ = drip_speed
            drip_falling = True
            if random.random() < prob_water:
                print('melt')
                icicle_length -= 1

        if random.random() < prob_water**2:
            print('freeze')
            # icicle_length += 1

        strip.show()
        time.sleep(delay)

def color_wheel2(time):
    section = math.floor(time*6) # an integer from 0 to 5
    up = time*6 % 1 # float 0 to 1, increasing with time
    slowup = up**9
    down = 1-up # float from 1 to 0
    slowdown = down**9
    red   = [       1,     down,   slowup, slowdown,       up,        1]
    green = [  slowup, slowdown,       up,        1,        1,     down]
    blue  = [      up,        1,        1,     down,   slowup, slowdown]
    return rgb_to_irgb((red[section], green[section], blue[section]))

def animate_rainbow(strip):
    speed_base = 1e-1
    speed_amp = 7e-2
    speed = 1 / 1100

    N = strip.numPixels()
    rainbow_center = 0

    def f_rainbow_center(x):
        # return 4*sin(2*pi*x) + 2*sin(6*pi*x) - sin(4*pi*x)
        return sin(2*pi*x) + sin(6*pi*x) - sin(4*pi*x)

    # these will be used to normalize f_rainbow_center
    max_c = max(f_rainbow_center(x/1000) for x in range(0, 1000))
    min_c = min(f_rainbow_center(x/1000) for x in range(0, 1000))

    for t in itertools.count():
        # normalize f_rainbow_center from its range to the LED range
        rainbow_center = mapp(f_rainbow_center(t * speed % 1), min_c, max_c, 0, N)

        for pixel_loc in range(strip.numPixels()):
            rainbow_loc = ((pixel_loc - rainbow_center) + N) % N
            color = color_wheel2(rainbow_loc / N)
            strip.setPixelColor(pixel_loc, color)

        strip.show()

# TODO: particle collision


strip = neopixel.Adafruit_NeoPixel(
    num=53, # number of pixels
    pin=18, # GPIO pin connected to the pixels (18 uses PWM!).
    strip_type=neopixel.ws.WS2812_STRIP,
)

strip.begin()
try:
    animate_rainbow(strip)
finally:
    for pixel in range(strip.numPixels()):
        strip.setPixelColor(pixel, black)
    strip._cleanup()
