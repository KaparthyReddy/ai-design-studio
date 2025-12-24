import torch
import torchvision.models as models
from pathlib import Path
import requests
from tqdm import tqdm

class ModelLoader:
    """Handles loading and caching of pre-trained models"""
    
    def __init__(self, models_dir):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        print(f"🎯 Using device: {self.device}")
    
    def load_vgg19(self):
        """Load VGG19 model for feature extraction"""
        print("📦 Loading VGG19 model...")
        
        vgg = models.vgg19(pretrained=True).features.to(self.device).eval()
        
        # Freeze all parameters
        for param in vgg.parameters():
            param.requires_grad_(False)
        
        print("✅ VGG19 loaded successfully")
        return vgg
    
    def load_vgg16(self):
        """Load VGG16 model (alternative for style transfer)"""
        print("📦 Loading VGG16 model...")
        
        vgg = models.vgg16(pretrained=True).features.to(self.device).eval()
        
        for param in vgg.parameters():
            param.requires_grad_(False)
        
        print("✅ VGG16 loaded successfully")
        return vgg
    
    def download_style_model(self, url, filename):
        """Download a pre-trained style model"""
        filepath = self.models_dir / filename
        
        if filepath.exists():
            print(f"✅ Model already exists: {filename}")
            return filepath
        
        print(f"⬇️  Downloading {filename}...")
        
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f, tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc=filename
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))
        
        print(f"✅ Downloaded: {filename}")
        return filepath
    
    def get_style_layers(self, model_type='vgg19'):
        """Get the layers to use for style and content"""
        if model_type == 'vgg19':
            # VGG19 layer indices for style transfer
            style_layers = {
                '0': 'conv1_1',
                '5': 'conv2_1',
                '10': 'conv3_1',
                '19': 'conv4_1',
                '28': 'conv5_1'
            }
            content_layers = {
                '21': 'conv4_2'
            }
        else:  # vgg16
            style_layers = {
                '0': 'conv1_1',
                '5': 'conv2_1',
                '10': 'conv3_1',
                '17': 'conv4_1',
                '24': 'conv5_1'
            }
            content_layers = {
                '19': 'conv4_2'
            }
        
        return style_layers, content_layers