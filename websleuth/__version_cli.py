import sys
from websleuth import __version__

def main():
    if '--version' in sys.argv:
        print(f"websleuth {__version__}")
    else:
        print("Run with --version to see the version.")
