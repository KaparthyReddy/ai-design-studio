import cv2
import numpy as np
from PIL import Image
import io
import base64

class ImageProcessor:
    """Utilities for image processing operations"""
    
    @staticmethod
    def resize_image(image_path, max_size=512, maintain_aspect=True):
        """
        Resize image to maximum dimension
        
        Args:
            image_path: Path to image file
            max_size: Maximum dimension (width or height)
            maintain_aspect: Keep aspect ratio
        
        Returns:
            PIL Image object
        """
        img = Image.open(image_path)
        
        if maintain_aspect:
            # Calculate new size maintaining aspect ratio
            ratio = min(max_size / img.size[0], max_size / img.size[1])
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        else:
            new_size = (max_size, max_size)
        
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        return img
    
    @staticmethod
    def image_to_base64(image_path):
        """Convert image file to base64 string"""
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    @staticmethod
    def base64_to_image(base64_string, output_path):
        """Convert base64 string to image file"""
        img_data = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_data))
        img.save(output_path)
        return output_path
    
    @staticmethod
    def create_thumbnail(image_path, size=(200, 200)):
        """Create thumbnail of image"""
        img = Image.open(image_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img
    
    @staticmethod
    def get_image_info(image_path):
        """Get basic information about an image"""
        img = Image.open(image_path)
        return {
            'width': img.size[0],
            'height': img.size[1],
            'format': img.format,
            'mode': img.mode,
            'size_bytes': image_path.stat().st_size if hasattr(image_path, 'stat') else None
        }
    
    @staticmethod
    def adjust_brightness(image_path, factor=1.2):
        """
        Adjust image brightness
        
        Args:
            image_path: Path to image
            factor: Brightness factor (1.0 = original, >1.0 = brighter, <1.0 = darker)
        """
        img = Image.open(image_path)
        img_array = np.array(img).astype(np.float32)
        img_array = np.clip(img_array * factor, 0, 255).astype(np.uint8)
        return Image.fromarray(img_array)
    
    @staticmethod
    def adjust_contrast(image_path, factor=1.2):
        """
        Adjust image contrast
        
        Args:
            factor: Contrast factor (1.0 = original)
        """
        img = Image.open(image_path)
        img_array = np.array(img).astype(np.float32)
        mean = img_array.mean()
        img_array = mean + factor * (img_array - mean)
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        return Image.fromarray(img_array)
    
    @staticmethod
    def extract_colors(image_path, num_colors=5):
        """
        Extract dominant colors from image
        
        Args:
            image_path: Path to image
            num_colors: Number of dominant colors to extract
        
        Returns:
            List of RGB tuples
        """
        img = Image.open(image_path)
        img = img.convert('RGB')
        img = img.resize((150, 150))  # Reduce size for faster processing
        
        img_array = np.array(img).reshape(-1, 3)
        
        # Use k-means clustering to find dominant colors
        from scipy.cluster.vq import kmeans, vq
        
        colors, _ = kmeans(img_array.astype(float), num_colors)
        colors = colors.astype(int)
        
        return [tuple(color) for color in colors]
    
    @staticmethod
    def blend_images(image1_path, image2_path, alpha=0.5):
        """
        Blend two images together
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            alpha: Blending factor (0.0 = all image1, 1.0 = all image2)
        """
        img1 = Image.open(image1_path).convert('RGB')
        img2 = Image.open(image2_path).convert('RGB')
        
        # Resize img2 to match img1
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
        
        # Blend
        blended = Image.blend(img1, img2, alpha)
        return blended
    
    @staticmethod
    def apply_filter(image_path, filter_type='sepia'):
        """
        Apply various filters to image
        
        Args:
            filter_type: 'sepia', 'grayscale', 'warm', 'cool'
        """
        img = Image.open(image_path).convert('RGB')
        img_array = np.array(img).astype(np.float32)
        
        if filter_type == 'sepia':
            sepia_filter = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            img_array = img_array @ sepia_filter.T
        
        elif filter_type == 'grayscale':
            gray = 0.2989 * img_array[:, :, 0] + \
                   0.5870 * img_array[:, :, 1] + \
                   0.1140 * img_array[:, :, 2]
            img_array = np.stack([gray, gray, gray], axis=-1)
        
        elif filter_type == 'warm':
            img_array[:, :, 0] *= 1.1  # Increase red
            img_array[:, :, 2] *= 0.9  # Decrease blue
        
        elif filter_type == 'cool':
            img_array[:, :, 0] *= 0.9  # Decrease red
            img_array[:, :, 2] *= 1.1  # Increase blue
        
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        return Image.fromarray(img_array)
    
    @staticmethod
    def create_preview(image_path, output_path, size=512):
        """Create a preview version of the image"""
        img = ImageProcessor.resize_image(image_path, max_size=size)
        img.save(output_path, quality=85, optimize=True)
        return output_path