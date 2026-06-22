import cv2
from pyzbar import pyzbar
from PIL import Image
import os
import sys

class BarcodeReader:
    def __init__(self):
        self.supported_image_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    
    def decode_image(self, image_path):
        """
        Decode barcodes from an image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            list: List of decoded barcode objects with data and type
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Check file extension
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in self.supported_image_formats:
            raise ValueError(f"Unsupported image format. Use: {self.supported_image_formats}")
        
        try:
            # Read image using OpenCV
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Decode barcodes
            decoded_objects = pyzbar.decode(img)
            
            # Prepare results
            results = []
            for obj in decoded_objects:
                results.append({
                    'data': obj.data.decode('utf-8'),
                    'type': obj.type,
                    'location': obj.rect,
                    'polygon': obj.polygon
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Error decoding barcode: {str(e)}")
    
    def decode_from_camera(self, camera_id=0, timeout=10):
        """
        Decode barcodes from camera feed
        
        Args:
            camera_id: Camera device ID (default: 0 for built-in camera)
            timeout: Timeout in seconds
            
        Returns:
            list: List of decoded barcode objects
        """
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            raise RuntimeError(f"Could not open camera with ID: {camera_id}")
        
        print("Press 's' to scan, 'q' to quit")
        
        scanned_codes = []
        start_time = cv2.getTickCount()
        
        while True:
            # Read frame from camera
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            # Decode barcodes in the frame
            decoded_objects = pyzbar.decode(frame)
            
            # Draw rectangles around detected barcodes
            for obj in decoded_objects:
                # Draw rectangle
                (x, y, w, h) = obj.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Add text
                text = f"{obj.data.decode('utf-8')} ({obj.type})"
                cv2.putText(frame, text, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Display the frame
            cv2.imshow('Barcode Scanner - Press "s" to scan, "q" to quit', frame)
            
            # Check for key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Scan the current frame
                if decoded_objects:
                    for obj in decoded_objects:
                        data = obj.data.decode('utf-8')
                        barcode_type = obj.type
                        scanned_codes.append({
                            'data': data,
                            'type': barcode_type,
                            'location': obj.rect
                        })
                        print(f"Scanned: {data} (Type: {barcode_type})")
                    print(f"Total scanned: {len(scanned_codes)} codes")
                else:
                    print("No barcode detected in the frame")
            
            # Check timeout
            elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
            if elapsed_time > timeout:
                print("Scanner timeout")
                break
        
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        
        return scanned_codes
    
    def decode_directory(self, directory_path):
        """
        Decode all barcodes from images in a directory
        
        Args:
            directory_path: Path to directory containing images
            
        Returns:
            dict: Dictionary mapping image paths to decoded barcodes
        """
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"Directory not found: {directory_path}")
        
        results = {}
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in self.supported_image_formats:
                try:
                    decoded = self.decode_image(file_path)
                    if decoded:
                        results[file_path] = decoded
                        print(f"Decoded {filename}: {len(decoded)} barcode(s)")
                    else:
                        print(f"No barcode found in {filename}")
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
        
        return results

if __name__ == "__main__":
    # Example usage
    reader = BarcodeReader()
    
    # Test with an image
    test_image = "generated_barcodes/test_barcode.png"
    if os.path.exists(test_image):
        results = reader.decode_image(test_image)
        for result in results:
            print(f"Decoded: {result['data']} (Type: {result['type']})")
    
    # Uncomment to test camera scanning
    # reader.decode_from_camera()
