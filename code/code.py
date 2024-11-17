import time
import board
import displayio
import digitalio
import busio
from adafruit_display_text import label
import terminalio
from adafruit_displayio_ssd1306 import SSD1306

# Display-Setup
displayio.release_displays()
i2c = busio.I2C(board.GP1, board.GP0)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = SSD1306(display_bus, width=128, height=32)

# Taster und Buzzer einrichten
button = digitalio.DigitalInOut(board.GP2)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

buzzer = digitalio.DigitalInOut(board.GP3)
buzzer.direction = digitalio.Direction.OUTPUT

# Timer-Variablen
main_timer = 0
second_timer = 0
second_timer_active = False
buzzer_active = False

# Zeitstempel initialisieren
last_main_timer_update = time.monotonic()
last_second_timer_update = time.monotonic()
last_buzzer_toggle = time.monotonic()
last_button_press_time = 0  # Für die Debounce-Logik

# Funktion zum Formatieren der Zeit hh:mm:ss
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Funktion zum Formatieren der Zeit mm:ss
def format_time_mm_ss(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

# Text für das Display
main_text = label.Label(
    terminalio.FONT,
    text=format_time(main_timer),
    color=0xFFFFFF,
    x=0,
    y=14,  # Position angepasst
    scale=2  # Größere Schrift
)
second_text = label.Label(
    terminalio.FONT,
    text="",  # Startet leer
    color=0xFFFFFF,
    x=97,
    y=10  # Position angepasst
)

# Display-Gruppe erstellen
display_group = displayio.Group()
display_group.append(main_text)
display_group.append(second_text)
display.root_group = display_group

while True:
    current_time = time.monotonic()

    # Haupttimer aktualisieren
    if current_time - last_main_timer_update >= 1:
        main_timer += 1
        main_text.text = format_time(main_timer)
        last_main_timer_update = current_time

    # Tasterabfrage mit Verzögerung zur Vermeidung von Doppelklicks
    if not button.value and (current_time - last_button_press_time > 1):
        last_button_press_time = current_time
        print("Taster wurde gedrückt")
        second_timer_active = not second_timer_active
        
        # Buzzer kurz ertönen lassen, wenn der Knopf gedrückt wird
        buzzer.value = True
        time.sleep(0.1)  # Piep-Ton für 0.1 Sekunden
        buzzer.value = False

        if second_timer_active:
            second_timer = 0
            last_second_timer_update = current_time
            second_text.text = format_time_mm_ss(second_timer)
        else:
            buzzer_active = False
            buzzer.value = False
            second_text.text = ""
        time.sleep(0.1)  # Kurze Verzögerung

    # Zweiten Timer aktualisieren
    if second_timer_active and (current_time - last_second_timer_update >= 1):
        second_timer += 1
        second_text.text = format_time_mm_ss(second_timer)
        last_second_timer_update = current_time

        if second_timer >= 60:
            buzzer_active = True

    # Buzzer steuern
    if buzzer_active and (current_time - last_buzzer_toggle >= 0.5):
        buzzer.value = not buzzer.value
        last_buzzer_toggle = current_time

    # Kurze Pause
    time.sleep(0.01)

