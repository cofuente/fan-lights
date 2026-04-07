import time
import subprocess
from openrgb import OpenRGBClient

# Ensure this path points to your framework_tool binary
FRAMEWORK_TOOL_PATH = "./framework_tool"

def update_framework_fan(colors):
    """Translates OpenRGB color objects into Framework hex commands."""
    # Convert OpenRGB color objects to '0xRRGGBB' hex strings
    # In this library version, color objects have .red, .green, .blue attributes
    hex_colors = [f"0x{c.red:02x}{c.green:02x}{c.blue:02x}" for c in colors]
    
    # The Mobius fan expects 8 LEDs. 
    # We pad with black (off) if fewer are provided, or trim if there are more.
    while len(hex_colors) < 8:
        hex_colors.append("0x000000")
    
    final_colors = hex_colors[:8]
    
    # Construct and run the command
    cmd = [FRAMEWORK_TOOL_PATH, "--rgbkbd", "0"] + final_colors
    
    try:
        # We use check=False because we don't want the script to crash 
        # if the tool returns a minor warning.
        subprocess.run(cmd, capture_output=True, check=False)
    except Exception as e:
        print(f"Failed to run framework_tool: {e}")

def main():
    try:
        client = OpenRGBClient(name="Framework Bridge")
        print("Connected to OpenRGB SDK!")
    except ConnectionRefusedError:
        print("Connection failed. Is OpenRGB open with the SDK Server started?")
        return

    while True:
        try:
            # Re-fetch the device list to ensure we stay synced
            devices = client.devices
            
            # Find our E1.31 dummy device
            fan_device = next((d for d in devices if "FrameworkFan" in d.name), None)
            
            if not fan_device:
                print("Looking for 'FrameworkFan' device... (Is it in the OpenRGB list?)")
                time.sleep(3)
                continue
            
            # THE FIX: Use the .colors property directly from the device object
            fan_device.update()          # <-- pull fresh state from the server
            current_colors = fan_device.colors
            
            if current_colors:
                update_framework_fan(current_colors)
            
            # 10Hz update rate (smooth enough for most effects)
            time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nBridge stopped by user.")
            break
        except Exception as e:
            print(f"Error during sync: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()