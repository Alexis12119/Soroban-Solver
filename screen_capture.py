import subprocess
import io
from PIL import Image

class ScreenCapture:
    def __init__(self):
        pass

    def capture_android_screen(self):
        """Capture screen from adb and convert to PIL Image"""
        try:
            # Use adb to capture the screen and pipe the output
            process = subprocess.Popen(
                ["adb", "exec-out", "screencap -p"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if stderr:
                print(f"ADB Error: {stderr.decode()}")
                return None

            # Convert the screencap data to a PIL Image
            image = Image.open(io.BytesIO(stdout))
            return image

        except FileNotFoundError:
            print("Error: ADB not found. Please ensure ADB is installed and in your system's PATH.")
            return None
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    def is_device_connected(self):
        """Check if an Android device is connected via ADB"""
        try:
            process = subprocess.Popen(
                ["adb", "devices"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if stderr:
                print(f"ADB Error: {stderr.decode()}")
                return False

            # Check if any devices are listed (excluding the header line)
            devices = stdout.decode().strip().split('\n')[1:]
            return len(devices) > 0

        except FileNotFoundError:
            print("Error: ADB not found. Please ensure ADB is installed and in your system's PATH.")
            return False
        except Exception as e:
            print(f"Error checking device connection: {e}")
            return False
