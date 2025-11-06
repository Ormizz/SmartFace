import RPi.GPIO as GPIO
import time

# Utilisation du mode BCM (numéros GPIO)
GPIO.setmode(GPIO.BCM)

# Définir les deux GPIOs
LED1 = 17
LED2 = 18

# Configuration des broches
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)

print("Test de deux LEDs (GPIO17 et GPIO18) — Ctrl+C pour arrêter")

try:
    while True:
        # Allume LED1, éteint LED2
        GPIO.output(LED1, GPIO.HIGH)
        GPIO.output(LED2, GPIO.LOW)
        time.sleep(0.5)

        # Inverse
        GPIO.output(LED1, GPIO.LOW)
        GPIO.output(LED2, GPIO.HIGH)
        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nGPIO nettoyé. Programme terminé.")
