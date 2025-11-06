#!/usr/bin/env python3
"""
Audio utilities for SmartFace
Helper functions to configure audio devices
"""

import subprocess
import re


def get_bluetooth_audio_devices():
    """
    Find Bluetooth audio device IDs
    
    Returns:
        dict: {'sink_id': int, 'source_id': int, 'sink_name': str, 'source_name': str}
    """
    try:
        result = subprocess.run(
            ['wpctl', 'status'],
            capture_output=True,
            text=True,
            timeout=5
        )
        status = result.stdout
    except Exception as e:
        print(f"⚠️  Could not get audio status: {e}")
        return {'sink_id': None, 'source_id': None, 'sink_name': None, 'source_name': None}
    
    devices = {
        'sink_id': None,
        'source_id': None,
        'sink_name': None,
        'source_name': None
    }
    
    # Find Bluetooth sink (speakers/headphones)
    sink_pattern = r'(\d+)\.\s+(.+bluez.+output.+)'
    match = re.search(sink_pattern, status, re.IGNORECASE)
    if match:
        devices['sink_id'] = int(match.group(1))
        devices['sink_name'] = match.group(2).strip()
    
    # Find Bluetooth source (microphone)
    source_pattern = r'(\d+)\.\s+(.+bluez.+input.+)'
    match = re.search(source_pattern, status, re.IGNORECASE)
    if match:
        devices['source_id'] = int(match.group(1))
        devices['source_name'] = match.group(2).strip()
    
    return devices


def set_bluetooth_as_default():
    """
    Set Bluetooth devices as default audio devices
    
    Returns:
        bool: True if successful, False otherwise
    """
    devices = get_bluetooth_audio_devices()
    
    if not devices['sink_id'] and not devices['source_id']:
        print("❌ No Bluetooth audio devices found")
        return False
    
    success = True
    
    # Set default speaker
    if devices['sink_id']:
        try:
            subprocess.run(
                ['wpctl', 'set-default', str(devices['sink_id'])],
                capture_output=True,
                timeout=5,
                check=True
            )
            print(f"✅ Bluetooth speaker set as default (ID: {devices['sink_id']})")
        except Exception as e:
            print(f"⚠️  Could not set default speaker: {e}")
            success = False
    
    # Set default microphone
    if devices['source_id']:
        try:
            subprocess.run(
                ['wpctl', 'set-default', str(devices['source_id'])],
                capture_output=True,
                timeout=5,
                check=True
            )
            print(f"✅ Bluetooth microphone set as default (ID: {devices['source_id']})")
        except Exception as e:
            print(f"⚠️  Could not set default microphone: {e}")
            success = False
    
    return success


def get_pyaudio_bluetooth_index():
    """
    Get PyAudio device index for Bluetooth microphone
    
    Returns:
        int or None: Device index if found, None otherwise
    """
    try:
        import pyaudio
    except ImportError:
        print("⚠️  PyAudio not installed")
        return None
    
    p = pyaudio.PyAudio()
    bluetooth_index = None
    
    try:
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            # Look for bluez device with input channels
            if 'bluez' in info['name'].lower() and info['maxInputChannels'] > 0:
                bluetooth_index = i
                print(f"✅ Found Bluetooth microphone at PyAudio index {i}: {info['name']}")
                break
    finally:
        p.terminate()
    
    return bluetooth_index


def ensure_bluetooth_headset_profile():
    """
    Ensure Bluetooth card is in headset profile (enables microphone)
    
    Returns:
        bool: True if successful or already set, False otherwise
    """
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
                
                # Set to headset_head_unit (enables microphone)
                subprocess.run(
                    ['pactl', 'set-card-profile', card_name, 'headset_head_unit'],
                    capture_output=True,
                    timeout=5
                )
                
                print(f"✅ Bluetooth profile set to headset mode")
                return True
        
        print("⚠️  No Bluetooth card found")
        return False
        
    except Exception as e:
        print(f"⚠️  Could not set Bluetooth profile: {e}")
        return False


def initialize_audio():
    """
    Complete audio initialization for SmartFace
    
    Returns:
        dict: Audio configuration {'bluetooth_index': int, 'devices': dict}
    """
    print("\n🎵 Initializing audio devices...")
    
    # Step 1: Set Bluetooth profile
    ensure_bluetooth_headset_profile()
    
    # Step 2: Find devices
    devices = get_bluetooth_audio_devices()
    
    if not devices['source_id']:
        print("❌ No Bluetooth microphone found!")
        print("   Make sure your Bluetooth device is connected")
        return None
    
    # Step 3: Set as default
    set_bluetooth_as_default()
    
    # Step 4: Get PyAudio index
    bluetooth_index = get_pyaudio_bluetooth_index()
    
    if bluetooth_index is None:
        print("⚠️  Could not find PyAudio device index")
        print("   Will try to use default device")
    
    config = {
        'bluetooth_index': bluetooth_index,
        'devices': devices
    }
    
    print("✅ Audio initialization complete\n")
    
    return config