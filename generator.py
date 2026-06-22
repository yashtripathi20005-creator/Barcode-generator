import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

class BarcodeGenerator:
    def __init__(self):
        self.supported_formats = ['code128', 'ean13', 'ean8', 'upc', 'qr']
        self.output_dir = "generated_barcodes"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_barcode(self, data, barcode_type='code128', filename=None, 
                         with_text=True, size=(300, 100)):
        """
        Generate a barcode image
        
        Args:
            data: Data to encode in the barcode
            barcode_type: Type of barcode (code128, ean13, ean8, upc, qr)
            filename: Output filename (without extension)
            with_text: Whether to include text below the barcode
            size: Size of the output image (width, height)
        
        Returns:
            str: Path to the generated barcode image
        """
        try:
            # Validate barcode type
            if barcode_type.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported barcode type. Choose from: {self.supported_formats}")
            
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"barcode_{barcode_type}_{timestamp}"
            
            # Ensure the file doesn't already exist
            output_path = os.path.join(self.output_dir, f"{filename}.png")
            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(self.output_dir, f"{filename}_{counter}.png")
                counter += 1
            
            # Create the barcode
            barcode_class = barcode.get_barcode_class(barcode_type)
            barcode_obj = barcode_class(data, writer=ImageWriter())
            
            # Generate the barcode image
            barcode_obj.save(output_path)
            
            # Add text to the image if requested
            if with_text:
                self._add_text_to_image(output_path, data)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error generating barcode: {str(e)}")
    
    def _add_text_to_image(self, image_path, text):
        """Add text below the barcode"""
        try:
            # Open the image
            img = Image.open(image_path)
            
            # Create a new image with more height for text
            new_height = img.height + 40
            new_img = Image.new('RGB', (img.width, new_height), 'white')
            
            # Paste the original barcode
            new_img.paste(img, (0, 0))
            
            # Add text
            draw = ImageDraw.Draw(new_img)
            
            # Try to use a default font or fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position (centered)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (img.width - text_width) // 2
            text_y = img.height + 10
            
            # Draw the text
            draw.text((text_x, text_y), text, fill='black', font=font)
            
            # Save the modified image
            new_img.save(image_path)
            
        except Exception as e:
            print(f"Warning: Could not add text to image: {str(e)}")
    
    def generate_batch(self, data_list, barcode_type='code128', with_text=True):
        """
        Generate multiple barcodes from a list of data
        
        Args:
            data_list: List of strings to encode
            barcode_type: Type of barcode to generate
            with_text: Whether to include text below the barcode
            
        Returns:
            list: List of paths to generated barcode images
        """
        generated_files = []
        for data in data_list:
            try:
                file_path = self.generate_barcode(
                    data, barcode_type, with_text=with_text
                )
                generated_files.append(file_path)
                print(f"Generated: {file_path}")
            except Exception as e:
                print(f"Error generating barcode for '{data}': {str(e)}")
        
        return generated_files

if __name__ == "__main__":
    # Example usage
    generator = BarcodeGenerator()
    
    # Generate a single barcode
    path = generator.generate_barcode("123456789", "code128", "test_barcode")
    print(f"Generated barcode: {path}")
    
    # Generate multiple barcodes
    data_list = ["ABCDEF", "987654321", "BARCODE123"]
    paths = generator.generate_batch(data_list, "code128")
    print(f"Generated {len(paths)} barcodes")
