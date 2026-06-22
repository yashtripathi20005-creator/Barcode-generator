import os
import json
from datetime import datetime
import shutil

class BarcodeUtils:
    """Utility functions for barcode operations"""
    
    @staticmethod
    def export_results(results, output_file, format='json'):
        """
        Export barcode decoding results to a file
        
        Args:
            results: List or dict of decoded barcode results
            output_file: Output file path
            format: Output format ('json' or 'txt')
        """
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        
        if format.lower() == 'json':
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
        elif format.lower() == 'txt':
            with open(output_file, 'w') as f:
                if isinstance(results, list):
                    for item in results:
                        f.write(f"Data: {item.get('data', 'N/A')} | Type: {item.get('type', 'N/A')}\n")
                elif isinstance(results, dict):
                    for key, value in results.items():
                        f.write(f"{key}:\n")
                        if isinstance(value, list):
                            for item in value:
                                f.write(f"  - Data: {item.get('data', 'N/A')} | Type: {item.get('type', 'N/A')}\n")
                        else:
                            f.write(f"  {value}\n")
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"Results exported to: {output_file}")
    
    @staticmethod
    def validate_barcode_data(data, barcode_type='code128'):
        """
        Validate data for specific barcode type
        
        Args:
            data: Data to validate
            barcode_type: Type of barcode
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not data:
            return False, "Data cannot be empty"
        
        data = str(data)
        
        if barcode_type.lower() == 'ean13':
            if not data.isdigit():
                return False, "EAN-13 must contain only digits"
            if len(data) != 12 and len(data) != 13:
                return False, "EAN-13 must be 12 or 13 digits"
        elif barcode_type.lower() == 'ean8':
            if not data.isdigit():
                return False, "EAN-8 must contain only digits"
            if len(data) != 7 and len(data) != 8:
                return False, "EAN-8 must be 7 or 8 digits"
        elif barcode_type.lower() == 'upc':
            if not data.isdigit():
                return False, "UPC must contain only digits"
            if len(data) != 11 and len(data) != 12:
                return False, "UPC must be 11 or 12 digits"
        
        return True, "Valid"
    
    @staticmethod
    def clean_output_directory(directory_path):
        """
        Remove all files in the output directory
        
        Args:
            directory_path: Path to the directory to clean
        """
        if os.path.exists(directory_path):
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Error removing {file_path}: {str(e)}")
            print(f"Cleaned directory: {directory_path}")
        else:
            print(f"Directory does not exist: {directory_path}")
    
    @staticmethod
    def get_barcode_info(image_path):
        """
        Get information about a barcode image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            dict: Information about the image
        """
        if not os.path.exists(image_path):
            return None
        
        stat = os.stat(image_path)
        info = {
            'filename': os.path.basename(image_path),
            'size_bytes': stat.st_size,
            'size_kb': round(stat.st_size / 1024, 2),
            'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'extension': os.path.splitext(image_path)[1].lower()
        }
        return info

if __name__ == "__main__":
    # Test utilities
    utils = BarcodeUtils()
    
    # Test validation
    valid, msg = utils.validate_barcode_data("123456789012", "ean13")
    print(f"EAN-13 validation: {valid} - {msg}")
    
    # Test cleaning
    # utils.clean_output_directory("generated_barcodes")
