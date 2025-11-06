#!/usr/bin/env python3
"""
Audio Device Initialization and Configuration
Detects and configures Bluetooth speakers/microphones before SmartFace starts
"""

import subprocess
import re
import time
import sys


class AudioDeviceManager:
    """Manage audio device detection and configuration"""
    
    def __init__(self):
        self.bt_sink_id = None
        self.bt_source_id = None
        self.bt_sink_name = None
        self.bt_source_name = None
    
    def get_wpctl_status(self):
        """Get wpctl status output"""
        try:
            result = subprocess.run(
                ['wpctl', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout
        except Exception as e:
            print(f"❌ Error getting wpctl status: {e}")
            return None
    
    def find_bluetooth_devices(self):
        """Find Bluetooth audio devices"""
        status = self.get_wpctl_status()
        if not status:
            return False
        
        print("\n" + "="*60)
        print("🔍 Searching for Bluetooth audio devices...")
        print("="*60 + "\n")
        
        # Find Bluetooth sink (speakers/headphones)
        sink_pattern = r'(\d+)\.\s+(.+bluez.+output.+)'
        for match in re.finditer(sink_pattern, status, re.IGNORECASE):
            self.bt_sink_id = match.group(1)
            self.bt_sink_name = match.group(2).strip()
            print(f"✅ Bluetooth Speaker found:")
            print(f"   ID: {self.bt_sink_id}")
            print(f"   Name: {self.bt_sink_name}\n")
            break
        
        # Find Bluetooth source (microphone)
        source_pattern = r'(\d+)\.\s+(.+bluez.+input.+)'
        for match in re.finditer(source_pattern, status, re.IGNORECASE):
            self.bt_source_id = match.group(1)
            self.bt_source_name = match.group(2).strip()
            print(f"✅ Bluetooth Microphone found:")
            print(f"   ID: {self.bt_source_id}")
            print(f"   Name: {self.bt_source_name}\n")
            break
        
        if not self.bt_sink_id and not self.bt_source_id:
            print("❌ No Bluetooth audio devices found!")
            print("\nMake sure your Bluetooth device is:")
            print("  1. Paired with bluetoothctl")
            print("  2. Connected")
            print("  3. Trusted\n")
            return False
        
        return True
    
    def set_bluetooth_profile(self):
        """Set Bluetooth card to headset profile (with microphone)"""
        try:
            # Get card list
            result = subprocess.run(
                ['pactl', 'list', 'cards', 'short'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Find bluez card
            for line in result.stdout.split('\n'):
                if 'bluez' in line.lower():
                    card_name = line.split()[1]
                    print(f"🔧 Setting Bluetooth profile to headset mode...")
                    
                    # Set to headset_head_unit (enables microphone)
                    subprocess.run(
                        ['pactl', 'set-card-profile', card_name, 'headset_head_unit'],
                        capture_output=True,
                        timeout=5
                    )
                    
                    time.sleep(1)  # Wait for profile switch
                    print("✅ Bluetooth profile configured\n")
                    return True
            
        except Exception as e:
            print(f"⚠️  Could not set Bluetooth profile: {e}")
            print("   Continuing anyway...\n")
        
        return False
    
    def set_default_devices(self):
        """Set Bluetooth devices as default"""
        success = True
        
        if self.bt_sink_id:
            print(f"🔊 Setting default speaker to ID {self.bt_sink_id}...")
            try:
                subprocess.run(
                    ['wpctl', 'set-default', self.bt_sink_id],
                    capture_output=True,
                    timeout=5,
                    check=True
                )
                print("✅ Default speaker configured\n")
            except Exception as e:
                print(f"❌ Failed to set default speaker: {e}\n")
                success = False
        
        if self.bt_source_id:
            print(f"🎙️  Setting default microphone to ID {self.bt_source_id}...")
            try:
                subprocess.run(
                    ['wpctl', 'set-default', self.bt_source_id],
                    capture_output=True,
                    timeout=5,
                    check=True
                )
                print("✅ Default microphone configured\n")
            except Exception as e:
                print(f"❌ Failed to set default microphone: {e}\n")
                success = False
        
        return success
    
    def test_speaker(self):
        """Test speaker output"""
        if not self.bt_sink_id:
            print("⚠️  No Bluetooth speaker to test\n")
            return False
        
        print("🔊 Testing speaker output...")
        print("   You should hear a test sound in 2 seconds...\n")
        time.sleep(2)
        
        try:
            subprocess.run(
                ['speaker-test', '-t', 'wav', '-c', '2', '-l', '1'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10
            )
            
            print("\n✅ Speaker test complete!")
            response = input("Did you hear the sound? (y/n): ").strip().lower()
            
            if response == 'y':
                print("✅ Speaker working correctly\n")
                return True
            else:
                print("❌ Speaker test failed\n")
                return False
                
        except Exception as e:
            print(f"❌ Speaker test error: {e}\n")
            return False
    
    def test_microphone(self):
        """Test microphone input"""
        if not self.bt_source_id:
            print("⚠️  No Bluetooth microphone to test\n")
            return False
        
        print("🎙️  Testing microphone...")
        print("   Recording 3 seconds... Speak now!\n")
        
        try:
            # Record 3 seconds
            subprocess.run(
                ['pw-record', '--target', self.bt_source_id, '/tmp/test-mic.wav'],
                timeout=3.5,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.TimeoutExpired:
            pass  # Expected - we want it to timeout after 3s
        except Exception as e:
            print(f"❌ Recording error: {e}\n")
            return False
        
        print("📢 Playing back your recording...\n")
        time.sleep(1)
        
        try:
            subprocess.run(
                ['pw-play', '--target', self.bt_sink_id, '/tmp/test-mic.wav'],
                timeout=10,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            print("✅ Microphone test complete!")
            response = input("Did you hear your voice? (y/n): ").strip().lower()
            
            if response == 'y':
                print("✅ Microphone working correctly\n")
                return True
            else:
                print("❌ Microphone test failed\n")
                return False
                
        except Exception as e:
            print(f"❌ Playback error: {e}\n")
            return False
    
    def show_current_devices(self):
        """Display currently configured devices"""
        print("\n" + "="*60)
        print("📋 Current Audio Configuration")
        print("="*60 + "\n")
        
        try:
            # Get default sink
            result = subprocess.run(
                ['wpctl', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            print("Current Devices:")
            
            # Parse and show sinks
            in_sinks = False
            in_sources = False
            
            for line in result.stdout.split('\n'):
                if 'Sinks:' in line:
                    in_sinks = True
                    in_sources = False
                    continue
                elif 'Sources:' in line:
                    in_sinks = False
                    in_sources = True
                    continue
                elif line.strip().startswith('├─') or line.strip().startswith('└─'):
                    in_sinks = False
                    in_sources = False
                
                if in_sinks and '*' in line:
                    print(f"  🔊 Speaker: {line.strip()}")
                
                if in_sources and '*' in line:
                    print(f"  🎙️  Microphone: {line.strip()}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error showing devices: {e}\n")
    
    def interactive_setup(self):
        """Interactive setup process"""
        print("\n" + "="*60)
        print("🎵 SmartFace Audio Device Initialization")
        print("="*60)
        
        # Step 1: Find devices
        if not self.find_bluetooth_devices():
            print("\n⚠️  Setup incomplete - no Bluetooth devices found")
            return False
        
        # Step 2: Set Bluetooth profile
        self.set_bluetooth_profile()
        
        # Step 3: Set as default
        if not self.set_default_devices():
            print("\n⚠️  Warning: Could not set default devices")
            print("   SmartFace may not work correctly\n")
        
        # Step 4: Show current config
        self.show_current_devices()
        
        # Step 5: Offer to test
        print("="*60)
        test_response = input("Do you want to test the devices? (y/n): ").strip().lower()
        
        if test_response == 'y':
            print()
            
            # Test speaker
            if self.bt_sink_id:
                self.test_speaker()
            
            # Test microphone
            if self.bt_source_id:
                self.test_microphone()
        
        print("="*60)
        print("✅ Audio initialization complete!")
        print("="*60 + "\n")
        
        return True
    
    def get_pyaudio_device_index(self):
        """Get PyAudio device index for Bluetooth microphone"""
        if not self.bt_source_name:
            return None
        
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            
            # Search for matching device
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if 'bluez' in info['name'].lower() and info['maxInputChannels'] > 0:
                    p.terminate()
                    return i
            
            p.terminate()
            
        except ImportError:
            print("⚠️  PyAudio not installed - cannot get device index")
        except Exception as e:
            print(f"⚠️  Error getting PyAudio index: {e}")
        
        return None


def main():
    """Main entry point"""
    manager = AudioDeviceManager()
    
    # Run interactive setup
    success = manager.interactive_setup()
    
    if success:
        # Export device info for SmartFace client
        if manager.bt_source_id:
            pyaudio_index = manager.get_pyaudio_device_index()
            if pyaudio_index is not None:
                print(f"📌 PyAudio device index: {pyaudio_index}")
                print(f"   Use this in your SmartFace client\n")
        
        sys.exit(0)
    else:
        print("\n❌ Audio initialization failed")
        print("   Please check your Bluetooth connection and try again\n")
        sys.exit(1)


if __name__ == "__main__":
    main()