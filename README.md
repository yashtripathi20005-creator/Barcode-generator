# 📦 Barcode Generator & Reader

A complete Python application to generate and read barcodes with support for multiple formats.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate a barcode
python main.py generate --data "123456789" --type code128 --output my_barcode

# Read barcode from image
python main.py read --image generated_barcodes/my_barcode.png

# Scan barcode from camera
python main.py read --camera

# Generate multiple barcodes
python main.py generate-batch --data "ABC123,DEF456,GHI789" --type code128

# Clean generated files
python main.py clean
