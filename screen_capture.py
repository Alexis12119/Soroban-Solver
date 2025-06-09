import subprocess
from PIL import Image
from io import BytesIO


class ScreenCapture:
    def __init__(self, timeout=5):
        self.timeout = timeout

    def capture_android_screen(self):
        """Capture Android screen using ADB"""
        try:
            result = subprocess.run(
                ['adb', 'exec-out', 'screencap', '-p'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.timeout
            )
            
            if result.returncode != 0 or not result.stdout:
                raise RuntimeError(f"ADB error: {result.stderr.decode().strip()}")
            
            return Image.open(BytesIO(result.stdout))
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Screen capture timed out after {self.timeout} seconds")
        except FileNotFoundError:
            raise RuntimeError("ADB not found. Make sure Android Debug Bridge is installed and in PATH")
        except Exception as e:
            raise RuntimeError(f"Failed to capture screen: {e}")

    def test_adb_connection(self):
        """Test if ADB connection is working"""
        try:
            result = subprocess.run(
                ['adb', 'devices'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=3
            )
            
            if result.returncode == 0:
                output = result.stdout.decode().strip()
                lines = output.split('\n')[1:]  # Skip header
                devices = [line for line in lines if line.strip() and 'device' in line]
                return len(devices) > 0, f"Found {len(devices)} device(s)"
            else:
                return False, f"ADB error: {result.stderr.decode().strip()}"
                
        except FileNotFoundError:
            return False, "ADB not found in PATH"
        except Exception as e:
            return False, f"Connection test failed: {e}"
