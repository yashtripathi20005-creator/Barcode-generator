import os
import sys
import argparse
from generator import BarcodeGenerator
from reader import BarcodeReader
from utils import BarcodeUtils

def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════╗
    ║     BARCODE GENERATOR & READER v1.0          ║
    ║           Python Application                 ║
    ╚═══════════════════════════════════════════════╝
    """
    print(banner)

def main():
    parser = argparse.ArgumentParser(
        description="Barcode Generator and Reader Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate barcode:
    python main.py generate --data "123456789" --type code128 --output my_barcode
    
  Read barcode from image:
    python main.py read --image generated_barcodes/my_barcode.png
    
  Read barcode from camera:
    python main.py read --camera
    
  Batch generate:
    python main.py generate-batch --data "123,456,789" --type code128
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate a barcode')
    generate_parser.add_argument('--data', required=True, help='Data to encode')
    generate_parser.add_argument('--type', default='code128', 
                                choices=['code128', 'ean13', 'ean8', 'upc', 'qr'],
                                help='Type of barcode')
    generate_parser.add_argument('--output', help='Output filename (without extension)')
    generate_parser.add_argument('--no-text', action='store_true', 
                                help='Do not include text below the barcode')
    
    # Read command
    read_parser = subparsers.add_parser('read', help='Read a barcode from image or camera')
    read_parser.add_argument('--image', help='Path to image file')
    read_parser.add_argument('--camera', action='store_true', help='Read from camera')
    read_parser.add_argument('--timeout', type=int, default=10, 
                            help='Timeout for camera scanning (seconds)')
    
    # Batch generate command
    batch_parser = subparsers.add_parser('generate-batch', help='Generate multiple barcodes')
    batch_parser.add_argument('--data', required=True, 
                             help='Comma-separated list of data to encode')
    batch_parser.add_argument('--type', default='code128',
                             choices=['code128', 'ean13', 'ean8', 'upc', 'qr'],
                             help='Type of barcode')
    batch_parser.add_argument('--no-text', action='store_true',
                             help='Do not include text below the barcode')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean generated barcodes')
    clean_parser.add_argument('--force', action='store_true', 
                             help='Force clean without confirmation')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print_banner()
    
    # Initialize components
    generator = BarcodeGenerator()
    reader = BarcodeReader()
    utils = BarcodeUtils()
    
    # Execute commands
    try:
        if args.command == 'generate':
            # Generate single barcode
            print(f"\nGenerating {args.type} barcode for data: {args.data}")
            
            # Validate data
            valid, msg = utils.validate_barcode_data(args.data, args.type)
            if not valid:
                print(f"Invalid data: {msg}")
                return
            
            output_path = generator.generate_barcode(
                data=args.data,
                barcode_type=args.type,
                filename=args.output,
                with_text=not args.no_text
            )
            print(f"✅ Barcode generated successfully!")
            print(f"📁 Saved to: {output_path}")
            
            # Show file info
            info = utils.get_barcode_info(output_path)
            if info:
                print(f"📊 File size: {info['size_kb']} KB")
            
        elif args.command == 'read':
            if args.image:
                # Read from image
                print(f"\nReading barcode from image: {args.image}")
                results = reader.decode_image(args.image)
                
                if results:
                    print(f"\n✅ Found {len(results)} barcode(s):")
                    for i, result in enumerate(results, 1):
                        print(f"  {i}. Data: {result['data']}")
                        print(f"     Type: {result['type']}")
                        print(f"     Location: {result['location']}")
                else:
                    print("❌ No barcode found in the image")
                    
            elif args.camera:
                # Read from camera
                print("\n📷 Starting camera scanner...")
                results = reader.decode_from_camera(timeout=args.timeout)
                
                if results:
                    print(f"\n✅ Scanned {len(results)} barcode(s):")
                    for i, result in enumerate(results, 1):
                        print(f"  {i}. Data: {result['data']}")
                        print(f"     Type: {result['type']}")
                else:
                    print("❌ No barcodes scanned")
            else:
                print("❌ Please specify --image or --camera")
                
        elif args.command == 'generate-batch':
            # Generate multiple barcodes
            data_list = [d.strip() for d in args.data.split(',') if d.strip()]
            
            print(f"\nGenerating {len(data_list)} barcodes of type: {args.type}")
            print(f"Data: {data_list}")
            
            # Validate all data
            valid_data = []
            for data in data_list:
                valid, msg = utils.validate_barcode_data(data, args.type)
                if valid:
                    valid_data.append(data)
                else:
                    print(f"⚠️ Skipping '{data}': {msg}")
            
            if not valid_data:
                print("❌ No valid data to process")
                return
            
            paths = generator.generate_batch(
                data_list=valid_data,
                barcode_type=args.type,
                with_text=not args.no_text
            )
            
            print(f"\n✅ Generated {len(paths)} barcodes successfully!")
            print("📁 Saved in: generated_barcodes/")
            
        elif args.command == 'clean':
            # Clean output directory
            if args.force or input("⚠️ Delete all generated barcodes? (y/n): ").lower() == 'y':
                utils.clean_output_directory("generated_barcodes")
                print("✅ Cleaned successfully!")
            else:
                print("❌ Clean cancelled")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
