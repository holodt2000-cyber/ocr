#!/usr/bin/env python3
"""Simple launcher for OCR tools."""

import sys
import os

def print_menu():
    print("\n" + "="*60)
    print("         OCR Tools - Interactive Launcher")
    print("="*60)
    print("\n1. [WEB] Web Editor (Recommended) - Browser-based editor")
    print("2. [OCR] Basic OCR - Recognize text from input.png")
    print("3. [POS] OCR with Positions - Get text coordinates")
    print("4. [EDT] Edit Text on Image - Replace/Remove/Highlight")
    print("5. [CHK] Check Installation - Verify dependencies")
    print("6. [DWN] Download Language Files - Get tessdata")
    print("0. [EXIT] Exit")
    print("\n" + "="*60)

def main():
    while True:
        print_menu()
        choice = input("\nSelect option (0-6): ").strip()
        
        if choice == '1':
            print("\n[*] Launching Web Editor...\n")
            print("Server will start at http://localhost:5000")
            print("Press Ctrl+C to stop the server\n")
            os.system("python web_app.py")
        
        elif choice == '2':
            image = input("Enter image path (or press Enter for input.png): ").strip()
            if not image:
                image = "input.png"
            print(f"\n[*] Running OCR on {image}...\n")
            os.system(f"python main.py {image}")
        
        elif choice == '3':
            image = input("Enter image path: ").strip()
            if not image:
                print("[!] Image path required!")
                continue
            mode = input("Mode (boxes/html/print/all) [all]: ").strip() or "all"
            print(f"\n[*] Running OCR with positions...\n")
            os.system(f"python ocr_with_positions.py {image} {mode}")
        
        elif choice == '4':
            image = input("Enter image path: ").strip()
            if not image:
                print("[!] Image path required!")
                continue
            
            print("\nCommands: replace, remove, highlight")
            command = input("Enter command: ").strip()
            
            if command == 'replace':
                old = input("Old text: ").strip()
                new = input("New text: ").strip()
                os.system(f'python edit_text_on_image.py "{image}" replace "{old}" "{new}"')
            elif command == 'remove':
                text = input("Text to remove: ").strip()
                os.system(f'python edit_text_on_image.py "{image}" remove "{text}"')
            elif command == 'highlight':
                text = input("Text to highlight: ").strip()
                color = input("Color (yellow/red/green) [yellow]: ").strip() or "yellow"
                os.system(f'python edit_text_on_image.py "{image}" highlight "{text}" {color}')
        
        elif choice == '5':
            print("\n[*] Checking installation...\n")
            os.system("python check_installation.py")
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            print("\n[*] Downloading language files...\n")
            langs = input("Languages (eng rus) [eng rus]: ").strip() or "eng rus"
            os.system(f"python download_tessdata.py {langs}")
            input("\nPress Enter to continue...")
        
        elif choice == '0':
            print("\n[*] Goodbye!\n")
            sys.exit(0)
        
        else:
            print("\n[!] Invalid option! Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Goodbye!\n")
        sys.exit(0)