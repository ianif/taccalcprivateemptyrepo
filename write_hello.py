#!/usr/bin/env python3
"""
A simple Python script that writes 'Hello' to a text file.
"""

__author__ = "IOANNA"

def write_hello_to_file(filename="output.txt", message="Hello"):
    """
    Write a message to a text file.
    
    Args:
        filename (str): The name of the output file (default: "output.txt")
        message (str): The message to write to the file (default: "Hello")
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Open the file in write mode (creates file if it doesn't exist)
        with open(filename, 'w') as file:
            # Write the message to the file
            file.write(message)
            print(f"Successfully wrote '{message}' to {filename}")
        return True
    except IOError as e:
        # Handle any file I/O errors
        print(f"Error writing to file: {e}")
        return False
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error: {e}")
        return False

def main():
    """
    Main function to execute the script.
    """
    # Call the function to write "Hello" to a text file
    success = write_hello_to_file("hello.txt", "Hello")
    
    if success:
        print("File operation completed successfully!")
    else:
        print("File operation failed.")

if __name__ == "__main__":
    # Execute the main function when script is run directly
    main()
