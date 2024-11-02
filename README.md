# CPR2BIN Converter

A Python utility for converting between Amstrad GX4000 cartridge ROM formats (CPR ↔ BIN).

## Description

This tool allows bi-directional conversion between:
- CPR format (Amstrad GX4000 cartridge ROM dump)
- BIN format (raw ROM data suitable for EPROM burning)

The CPR format is based on RIFF and consists of 16KB blocks with specific headers. This utility handles all the necessary format conversion while maintaining data integrity.

## Features

- Bi-directional conversion (CPR → BIN and BIN → CPR)
- Handles multiple 16KB blocks
- Automatic block padding
- Validates file format and headers
- Enforces format constraints (max 512KB/32 blocks)

## Requirements

- Python 3.6 or higher

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/cpr2bin.git
cd cpr2bin
```

2. Make the script executable (Unix-like systems):
```bash
chmod +x cpr2bin.py
```

## Usage

### Converting CPR to BIN

```bash
python3 cpr2bin.py --to-bin input.cpr output.bin
```

### Converting BIN to CPR

```bash
python3 cpr2bin.py --to-cpr input.bin output.cpr
```

### Command-line Arguments

```
Usage: cpr2bin.py <direction> <input_file> <output_file>
  direction: --to-bin or --to-cpr
```

## Technical Details

### CPR Format Structure
- RIFF header (4 bytes)
- File size (4 bytes)
- AMS! identifier (4 bytes)
- Multiple 16KB blocks, each with:
  - Block identifier (4 bytes, "cbXX")
  - Block size (4 bytes)
  - Block data (up to 16KB)

### Limitations
- Maximum file size: 512KB (32 blocks of 16KB each)
- Block size: Fixed at 16KB (padded with zeros if necessary)
