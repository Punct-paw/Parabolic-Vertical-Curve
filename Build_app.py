import os
import subprocess

def build_app():
    try:
        # Ensure both files are in the current directory
        if not os.path.exists("GUIFile.py") or not os.path.exists("parabolic.py"):
            raise FileNotFoundError("Ensure GUI File.py and parabolic.py are in the current directory")

        # PyInstaller command to build the executable
        command = [
            "pyinstaller",
            "--onefile",  # Create a single executable file
            "--windowed",  # Run as a GUI application (no console on Windows)
            "--name=VerticalParabolicCurveCalculator",  # Name of the executable
            "--add-data=parabolic.py;.",  # Include parabolic.py (syntax for Windows; use : for macOS/Linux)
            "--clean"   #Clear cache for fresh build
            "GUIFile.py"  # Main script
        ]

        # Run PyInstaller
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Build successful! Executable createsd in dist/VerticalCurveCalculator")
        print(result.stdout)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller failed: {e}")
        print(e.stderr)
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    build_app()
