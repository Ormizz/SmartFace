import json
from smartface.config import SMART_HOME_DEVICES


class SmartHomeSkill:
    """
    Smart home control skill (simulation)
    Controls virtual devices
    """
    
    def __init__(self):
        print("🔧 Initializing Smart Home skill...")
        
        # Load device states (in-memory simulation)
        self.devices = SMART_HOME_DEVICES.copy()
        
        print(f"✅ Smart Home ready ({len(self.devices)} devices)")
    
    def turn_on_light(self, room=None):
        """
        Turn on light in specified room
        
        Args:
            room: Room name (e.g., 'living room')
            
        Returns:
            str: Confirmation message
        """
        if not room:
            # Turn on all lights
            count = 0
            for device_name, device in self.devices.items():
                if device['type'] == 'light':
                    device['state'] = 'on'
                    device['brightness'] = 100
                    count += 1
            return f"Turned on {count} light{'s' if count != 1 else ''}."
        
        # Turn on specific room light
        device_key = f"{room.replace(' ', '_')}_light"
        
        if device_key in self.devices:
            self.devices[device_key]['state'] = 'on'
            self.devices[device_key]['brightness'] = 100
            return f"Turned on the {room} light."
        else:
            return f"I couldn't find a light in the {room}. Available rooms: living room, bedroom."
    
    def turn_off_light(self, room=None):
        """
        Turn off light in specified room
        
        Args:
            room: Room name
            
        Returns:
            str: Confirmation message
        """
        if not room:
            # Turn off all lights
            count = 0
            for device_name, device in self.devices.items():
                if device['type'] == 'light':
                    device['state'] = 'off'
                    device['brightness'] = 0
                    count += 1
            return f"Turned off {count} light{'s' if count != 1 else ''}."
        
        # Turn off specific room light
        device_key = f"{room.replace(' ', '_')}_light"
        
        if device_key in self.devices:
            self.devices[device_key]['state'] = 'off'
            self.devices[device_key]['brightness'] = 0
            return f"Turned off the {room} light."
        else:
            return f"I couldn't find a light in the {room}."
    
    def set_brightness(self, brightness, room=None):
        """
        Set light brightness
        
        Args:
            brightness: Brightness level (0-100)
            room: Room name (optional)
            
        Returns:
            str: Confirmation message
        """
        brightness = max(0, min(100, brightness))  # Clamp to 0-100
        
        if not room:
            # Set all lights
            count = 0
            for device_name, device in self.devices.items():
                if device['type'] == 'light':
                    device['brightness'] = brightness
                    device['state'] = 'on' if brightness > 0 else 'off'
                    count += 1
            return f"Set brightness to {brightness}% for {count} light{'s' if count != 1 else ''}."
        
        device_key = f"{room.replace(' ', '_')}_light"
        
        if device_key in self.devices:
            self.devices[device_key]['brightness'] = brightness
            self.devices[device_key]['state'] = 'on' if brightness > 0 else 'off'
            return f"Set {room} light brightness to {brightness}%."
        else:
            return f"I couldn't find a light in the {room}."
    
    def set_temperature(self, temperature):
        """
        Set thermostat temperature
        
        Args:
            temperature: Target temperature in Celsius
            
        Returns:
            str: Confirmation message
        """
        if temperature < 10 or temperature > 35:
            return "Temperature should be between 10 and 35 degrees Celsius."
        
        if 'thermostat' in self.devices:
            self.devices['thermostat']['temperature'] = temperature
            self.devices['thermostat']['state'] = 'on'
            return f"Set thermostat to {temperature} degrees Celsius."
        else:
            return "I couldn't find the thermostat."
    
    def get_status(self):
        """
        Get status of all devices
        
        Returns:
            str: Device status summary
        """
        status_parts = ["Here's your smart home status:"]
        
        # Lights
        lights_on = []
        lights_off = []
        for device_name, device in self.devices.items():
            if device['type'] == 'light':
                room = device_name.replace('_light', '').replace('_', ' ')
                if device['state'] == 'on':
                    brightness = device.get('brightness', 100)
                    lights_on.append(f"{room} ({brightness}%)")
                else:
                    lights_off.append(room)
        
        if lights_on:
            status_parts.append(f"Lights on: {', '.join(lights_on)}")
        if lights_off:
            status_parts.append(f"Lights off: {', '.join(lights_off)}")
        
        # Thermostat
        if 'thermostat' in self.devices:
            thermostat = self.devices['thermostat']
            temp = thermostat.get('temperature', 20)
            state = thermostat.get('state', 'off')
            status_parts.append(f"Thermostat: {temp}°C ({state})")
        
        # Other devices
        for device_name, device in self.devices.items():
            if device['type'] not in ['light', 'thermostat']:
                name = device_name.replace('_', ' ')
                state = device.get('state', 'unknown')
                status_parts.append(f"{name}: {state}")
        
        return "\n".join(status_parts)
    
    def open_garage(self):
        """Open garage door"""
        if 'garage_door' in self.devices:
            self.devices['garage_door']['state'] = 'open'
            return "Opening garage door."
        return "Garage door not found."
    
    def close_garage(self):
        """Close garage door"""
        if 'garage_door' in self.devices:
            self.devices['garage_door']['state'] = 'closed'
            return "Closing garage door."
        return "Garage door not found."