import subprocess
import sys

# list of packages to ensure are installed
packages = [
    "pyrebase4",
    "pyqt5",
    "nltk",
    "pyaudio",
    "librosa",
    "torch"
]

def install_packages():
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")

def main():
    # ensure required packages are installed
    install_packages()

    print("Running the main program...")

if __name__ == "__main__":
    main()