
import sys
from pathlib import Path

# Add src to sys.path
root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir / "src"))

from goldsense.tonl import decode_tonl

def test_escapes():
    # Simulate a line from the file
    # This represents: "Line1\nLine2" encoded as "Line1\nLine2" string literal in keys
    input_text = r'''#version 1.0
news[1]{content}:
  "Line1\nLine2"'''
    
    print(f"Input text raw:\n{input_text}")
    print("-" * 20)
    
    decoded = decode_tonl(input_text)
    print(f"Decoded object: {decoded}")
    
    content = decoded['news'][0]['content']
    print(f"Content repr: {repr(content)}")
    
    if content == "Line1\nLine2":
        print("SUCCESS: Newline decoded correctly.")
    elif content == "Line1\\nLine2":
        print("FAILURE: Newline remained escaped.")
    else:
        print(f"FAILURE: Unexpected content: {repr(content)}")

if __name__ == "__main__":
    test_escapes()
