#!/usr/bin/env python3
import sys
import struct
from pathlib import Path

def convert_cpr_to_bin(input_file: str, output_file: str) -> None:
    """Convert a CPR format file to raw binary format.
    
    Args:
        input_file: Path to input CPR file
        output_file: Path to output BIN file
    """
    try:
        with open(input_file, 'rb') as cpr:
            # Verify RIFF header
            riff_header = cpr.read(4)
            if riff_header != b'RIFF':
                raise ValueError("Not a valid RIFF file")
            
            # Read file size (minus 8 bytes for RIFF header)
            total_size = struct.unpack('<I', cpr.read(4))[0]
            
            # Verify AMS! form type
            form_type = cpr.read(4)
            if form_type != b'AMS!':
                raise ValueError("Not a valid CPR file (missing Ams! identifier)")
            
            # Process chunks
            blocks = {}  # Store blocks indexed by their number
            
            while cpr.tell() < total_size + 8:  # +8 because total_size excludes RIFF header
                # Read chunk header
                chunk_id = cpr.read(4)
                chunk_size = struct.unpack('<I', cpr.read(4))[0]
                
                if not chunk_id.startswith(b'cb'):
                    # Skip non-cartridge blocks
                    cpr.seek(chunk_size, 1)  # 1 means relative to current position
                    continue
                
                # Extract block number from chunk ID (e.g., 'cb00' -> 0)
                block_num = int(chunk_id[2:].decode())
                
                # Read block data
                block_data = cpr.read(min(chunk_size, 16384))  # Read max 16KB
                blocks[block_num] = block_data
                
                # Skip any remaining chunk data if > 16KB
                if chunk_size > 16384:
                    cpr.seek(chunk_size - 16384, 1)
            
            # Write blocks in order to output file
            with open(output_file, 'wb') as bin_file:
                for block_num in sorted(blocks.keys()):
                    data = blocks[block_num]
                    # Pad block to 16KB if necessary
                    if len(data) < 16384:
                        data = data + b'\x00' * (16384 - len(data))
                    bin_file.write(data)
                    
            print(f"Successfully converted {input_file} to {output_file}")
            print(f"Processed {len(blocks)} blocks of 16KB each")
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")

def main():
    if len(sys.argv) != 3:
        print("Usage: cpr2bin.py input.cpr output.bin")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_cpr_to_bin(input_file, output_file)

if __name__ == "__main__":
    main() 