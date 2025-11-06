"""
LED Controller for Raspberry Pi
Controls status LEDs during voice interaction
"""

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("⚠️  RPi.GPIO not available - LED control disabled")


class LEDController:
    """
    Control status LEDs on Raspberry Pi
    - Blue LED: Listening (recording audio)
    - Red LED: Processing / Idle
    """
    
    # GPIO Pin numbers (BCM mode)
    BLUE_LED_PIN = 17   # GPIO 17 (Physical pin 11)
    RED_LED_PIN = 27    # GPIO 18 (Physical pin 13)
    
    def __init__(self):
        self.enabled = GPIO_AVAILABLE
        
        if not self.enabled:
            print("🔴 LED Controller: Disabled (not on Raspberry Pi)")
            return
        
        try:
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup pins as outputs
            GPIO.setup(self.BLUE_LED_PIN, GPIO.OUT)
            GPIO.setup(self.RED_LED_PIN, GPIO.OUT)
            
            # Start with red LED on (idle state)
            self.set_idle()
            
            print("✅ LED Controller: Initialized")
            print(f"   Blue LED: GPIO {self.BLUE_LED_PIN}")
            print(f"   Red LED:  GPIO {self.RED_LED_PIN}")
        
        except Exception as e:
            print(f"⚠️  LED Controller: Init failed - {e}")
            self.enabled = False
    
    def set_listening(self):
        """Blue LED ON - listening/recording"""
        if not self.enabled:
            return
        try:
            GPIO.output(self.BLUE_LED_PIN, GPIO.HIGH)
            GPIO.output(self.RED_LED_PIN, GPIO.LOW)
        except:
            pass
    
    def set_processing(self):
        """Red LED ON - processing/thinking"""
        if not self.enabled:
            return
        try:
            GPIO.output(self.BLUE_LED_PIN, GPIO.LOW)
            GPIO.output(self.RED_LED_PIN, GPIO.HIGH)
        except:
            pass
    
    def set_idle(self):
        """Red LED ON - idle/ready"""
        self.set_processing()  # Same as processing
    
    def set_error(self):
        """Both LEDs blink - error state"""
        if not self.enabled:
            return
        try:
            for _ in range(3):
                GPIO.output(self.BLUE_LED_PIN, GPIO.HIGH)
                GPIO.output(self.RED_LED_PIN, GPIO.HIGH)
                import time
                time.sleep(0.2)
                GPIO.output(self.BLUE_LED_PIN, GPIO.LOW)
                GPIO.output(self.RED_LED_PIN, GPIO.LOW)
                time.sleep(0.2)
            self.set_idle()
        except:
            pass
    
    def all_off(self):
        """Turn off all LEDs"""
        if not self.enabled:
            return
        try:
            GPIO.output(self.BLUE_LED_PIN, GPIO.LOW)
            GPIO.output(self.RED_LED_PIN, GPIO.LOW)
        except:
            pass
    
    def cleanup(self):
        """Cleanup GPIO on exit"""
        if not self.enabled:
            return
        try:
            self.all_off()
            GPIO.cleanup()
            print("🔧 LED Controller: Cleaned up")
        except:
            pass