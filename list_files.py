import os

def list_files(directory):
    print(f"Listing files in {directory}:")
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                print(f"[DIR] {item}")
            else:
                print(f"[FILE] {item}")
    except Exception as e:
        print(f"Error: {e}")

# List files in current directory
print("Current directory:", os.getcwd())
list_files(".")

# List files in migrations directory
list_files("migrations")

# List files in news_crawler directory
list_files("news_crawler")
