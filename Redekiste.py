# Verbesserte Version: Sperrt Taster waehrend des Druckvorgangs

from gpiozero import Button, LED
from signal import pause
import time
import random
import os
import threading
from escpos import *

# === GPIO Setup ===
person_buttons = {
    'A': Button(5, pull_up=True, bounce_time=0.1),
    'B': Button(11, pull_up=True, bounce_time=0.1),
    'C': Button(9, pull_up=True, bounce_time=0.1)
}
person_leds = {
    'A': LED(4),
    'B': LED(3),
    'C': LED(2)
}

mood_buttons = {
    '1': Button(19, pull_up=True, bounce_time=0.1),
    '2': Button(26, pull_up=True, bounce_time=0.1),
    '3': Button(13, pull_up=True, bounce_time=0.1),
    '4': Button(6, pull_up=True, bounce_time=0.1)
}
mood_leds = {
    '1': LED(10),
    '2': LED(22),
    '3': LED(27),
    '4': LED(17)
}

# === Statusvariablen ===
selected_person = None
selected_mood = None
printing = False
attracting = False
blink_thread = None

p = printer.Usb(0x0456, 0x0808, in_ep=0x81, out_ep=0x03)

# === Blinkanimation ===
def attract_loop():
    def blink():
        while attracting:
            if selected_person or selected_mood:
                break
            for led in list(person_leds.values()) + list(mood_leds.values()):
                if selected_person or selected_mood:
                    break
                led.on()
                time.sleep(0.1)
                led.off()
            time.sleep(0.5)
    global blink_thread
    blink_thread = threading.Thread(target=blink)
    blink_thread.daemon = True
    blink_thread.start()

# === Reset-Funktion ===
def reset_all():
    global selected_person, selected_mood, printing, attracting
    selected_person = None
    selected_mood = None
    printing = False
    attracting = True
    for led in person_leds.values():
        led.off()
    for led in mood_leds.values():
        led.off()
    attract_loop()

# === Drucksimulation ===
def simulate_print():
    global selected_person, selected_mood, printing, attracting, p
    printing = True
    attracting = False
    print(f"Simuliere Ausgabe: Auswahl war Person '{selected_person}' und Stimmung '{selected_mood}'")
    p.image(f"{selected_person}{selected_mood}.jpg")
    p.text("\n\n")
    time.sleep(5)
    reset_all()

# === Handler-Funktionen ===
def make_person_handler(key):
    def handler():
        global selected_person, attracting
        print(f"Pressed Person button {key}. Printing: {printing}. Selected Mood: {selected_mood}")
        if printing:
            return
        selected_person = key
        attracting = False
        for k, led in person_leds.items():
            led.on() if k == selected_person else led.off()
        if selected_person and selected_mood:
            simulate_print()
    return handler

def make_mood_handler(key):
    def handler():
        global selected_mood, attracting
        print(f"Pressed Mood button {key}. Printing: {printing}. Selected Person: {selected_person}")
        if printing:
            return
        selected_mood = key
        attracting = False
        for k, led in mood_leds.items():
            led.on() if k == selected_mood else led.off()
        if selected_person and selected_mood:
            simulate_print()
    return handler

# === Events zuweisen ===
for k in person_buttons:
    person_buttons[k].when_pressed = make_person_handler(k)
for k in mood_buttons:
    mood_buttons[k].when_pressed = make_mood_handler(k)

# === Start ===
reset_all()
print("Testmodus ohne Druck aktiv - Leuchten und Taster werden getestet.")
pause()
