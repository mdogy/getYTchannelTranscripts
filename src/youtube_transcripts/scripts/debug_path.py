import sys
import os


def main():
    """Prints the Python path and current working directory."""
    print("--- sys.path ---")
    for p in sys.path:
        print(p)
    print("\n--- CWD ---")
    print(os.getcwd())


if __name__ == "__main__":
    main()
