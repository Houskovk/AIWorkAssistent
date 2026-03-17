import sys
import pyttsx3
import argparse

def generate_speech(text, output_file):
    try:
        engine = pyttsx3.init()
        
        # Save to file
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        print(f"SUCCESS: {output_file}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text to speak")
    group.add_argument("--file", help="File containing text to speak")
    
    parser.add_argument("--output", required=True, help="Output audio file path")
    
    args = parser.parse_args()
    
    text = args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
            
    generate_speech(text, args.output)
