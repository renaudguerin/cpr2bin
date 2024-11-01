#!/usr/bin/env python3
import sys
import struct
from pathlib import Path
from typing import Dict, Optional

# Constants
BLOCK_SIZE = 16384  # 16KB
RIFF_HEADER = b'RIFF'
CPR_FORM_TYPE = b'AMS!'
CHUNK_PREFIX = b'cb'

class ConversionError(Exception):
    """Custom exception for conversion errors"""
    pass

def read_cpr_blocks(cpr_file) -> Dict[int, bytes]:
    """Read blocks from a CPR file.
    
    Args:
        cpr_file: Open file handle in binary read mode
        
    Returns:
        Dictionary mapping block numbers to their data
    """
    # Verify RIFF header
    if cpr_file.read(4) != RIFF_HEADER:
        raise ConversionError("Not a valid RIFF file")
    
    # Read file size (minus 8 bytes for RIFF header)
    total_size = struct.unpack('<I', cpr_file.read(4))[0]
    
    # Verify AMS! form type
    if cpr_file.read(4) != CPR_FORM_TYPE:
        raise ConversionError("Not a valid CPR file (missing AMS! identifier)")
    
    blocks = {}
    while cpr_file.tell() < total_size + 8:
        # Read chunk header
        chunk_id = cpr_file.read(4)
        chunk_size = struct.unpack('<I', cpr_file.read(4))[0]
        
        if not chunk_id.startswith(CHUNK_PREFIX):
            # Skip non-cartridge blocks
            cpr_file.seek(chunk_size, 1)
            continue
        
        # Extract block number from chunk ID (e.g., 'cb00' -> 0)
        block_num = int(chunk_id[2:].decode())
        
        # Read block data
        block_data = cpr_file.read(min(chunk_size, BLOCK_SIZE))
        blocks[block_num] = block_data
        
        # Skip any remaining chunk data if > 16KB
        if chunk_size > BLOCK_SIZE:
            cpr_file.seek(chunk_size - BLOCK_SIZE, 1)
    
    return blocks

def write_cpr_file(blocks: Dict[int, bytes], output_file) -> None:
    """Write blocks to a CPR file.
    
    Args:
        blocks: Dictionary mapping block numbers to their data
        output_file: Open file handle in binary write mode
    """
    # Calculate total size (4 bytes form type + sum of all chunk sizes with headers)
    total_size = 4  # Form type
    for data in blocks.values():
        total_size += 8 + len(data)  # 8 bytes for chunk header
    
    # Write RIFF header
    output_file.write(RIFF_HEADER)
    output_file.write(struct.pack('<I', total_size))
    output_file.write(CPR_FORM_TYPE)
    
    # Write blocks
    for block_num in sorted(blocks.keys()):
        data = blocks[block_num]
        chunk_id = f"{CHUNK_PREFIX.decode()}{block_num:02d}".encode()
        output_file.write(chunk_id)
        output_file.write(struct.pack('<I', len(data)))
        output_file.write(data)

def convert_cpr_to_bin(input_file: str, output_file: str) -> None:
    """Convert a CPR format file to raw binary format."""
    try:
        with open(input_file, 'rb') as cpr:
            blocks = read_cpr_blocks(cpr)
            
        with open(output_file, 'wb') as bin_file:
            for block_num in sorted(blocks.keys()):
                data = blocks[block_num]
                # Pad block to 16KB if necessary
                if len(data) < BLOCK_SIZE:
                    data = data + b'\x00' * (BLOCK_SIZE - len(data))
                bin_file.write(data)
        
        print(f"Successfully converted {input_file} to {output_file}")
        print(f"Processed {len(blocks)} blocks of 16KB each")
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
    except ConversionError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")

def convert_bin_to_cpr(input_file: str, output_file: str) -> None:
    """Convert a raw binary file to CPR format."""
    try:
        # Read the binary file
        with open(input_file, 'rb') as bin_file:
            bin_data = bin_file.read()
        
        # Calculate number of blocks needed
        total_blocks = (len(bin_data) + BLOCK_SIZE - 1) // BLOCK_SIZE
        if total_blocks > 32:
            raise ConversionError("Input file too large (max 32 blocks / 512KB supported)")
        
        # Create blocks dictionary
        blocks = {}
        for block_num in range(total_blocks):
            start = block_num * BLOCK_SIZE
            end = start + BLOCK_SIZE
            block_data = bin_data[start:end]
            if len(block_data) > 0:  # Only store non-empty blocks
                blocks[block_num] = block_data
        
        # Write CPR file
        with open(output_file, 'wb') as cpr:
            write_cpr_file(blocks, cpr)
        
        print(f"Successfully converted {input_file} to {output_file}")
        print(f"Created {len(blocks)} blocks of up to 16KB each")
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
    except ConversionError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")

def main():
    if len(sys.argv) != 4:
        print("Usage: cpr2bin.py <direction> <input_file> <output_file>")
        print("  direction: --to-bin or --to-cpr")
        sys.exit(1)
    
    direction = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    if direction == '--to-bin':
        convert_cpr_to_bin(input_file, output_file)
    elif direction == '--to-cpr':
        convert_bin_to_cpr(input_file, output_file)
    else:
        print("Error: Invalid direction. Use --to-bin or --to-cpr")
        sys.exit(1)

if __name__ == "__main__":
    main() 