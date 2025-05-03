import os
import sys

print("Current working directory:", os.getcwd())

try:
    print("Contents of migrations directory:")
    for item in os.listdir("migrations"):
        print(f"- {item}")
except Exception as e:
    print(f"Error accessing migrations directory: {e}")
