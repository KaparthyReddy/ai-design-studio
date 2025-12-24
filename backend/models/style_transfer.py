import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from PIL import Image
import copy

class StyleTransferModel:
    """Neural Style Transfer using VGG19"""
    
    def __init__(self, model_loader, image_size=512):
        self.device = model_loader.device
        self.vgg = model_loader.load_vgg19()
        self.image_size = image_size
        self.style_layers, self.content_layers = model_loader.get_style_layers()
        
        # Normalization for VGG
        self.normalization_mean = torch.tensor([0.485, 0.456, 0.406]).to(self.device)
        self.normalization_std = torch.tensor([0.229, 0.224, 0.225]).to(self.device)
    
    def load_image(self, image_path):
        """Load and preprocess image"""
        image = Image.open(image_path).convert('RGB')
        
        # Resize maintaining aspect ratio
        aspect_ratio = image.size[0] / image.size[1]
        if aspect_ratio > 1:
            new_size = (self.image_size, int(self.image_size / aspect_ratio))
        else:
            new_size = (int(self.image_size * aspect_ratio), self.image_size)
        
        transform = transforms.Compose([
            transforms.Resize(new_size),
            transforms.ToTensor(),
        ])
        
        image = transform(image).unsqueeze(0)
        return image.to(self.device)
    
    def save_image(self, tensor, output_path):
        """Save tensor as image"""
        image = tensor.cpu().clone()
        image = image.squeeze(0)
        image = transforms.ToPILImage()(image)
        image.save(output_path)
        return image
    
    def gram_matrix(self, input_tensor):
        """Calculate Gram Matrix for style representation"""
        batch_size, channels, height, width = input_tensor.size()
        features = input_tensor.view(batch_size * channels, height * width)
        gram = torch.mm(features, features.t())
        return gram.div(batch_size * channels * height * width)
    
    def get_features(self, image, model):
        """Extract features from specific layers"""
        features = {}
        x = image
        
        for name, layer in model._modules.items():
            x = layer(x)
            if name in self.style_layers or name in self.content_layers:
                features[name] = x
        
        return features
    
    def transfer_style(self, content_path, style_path, output_path, 
                       num_steps=300, style_weight=1000000, content_weight=1,
                       callback=None):
        """
        Perform style transfer
        
        Args:
            content_path: Path to content image
            style_path: Path to style image
            output_path: Path to save output
            num_steps: Number of optimization steps
            style_weight: Weight for style loss
            content_weight: Weight for content loss
            callback: Optional callback function for progress updates
        """
        print("🎨 Starting style transfer...")
        
        # Load images
        content_img = self.load_image(content_path)
        style_img = self.load_image(style_path)
        
        # Start with content image (or use random noise)
        input_img = content_img.clone()
        
        # Get features
        content_features = self.get_features(content_img, self.vgg)
        style_features = self.get_features(style_img, self.vgg)
        
        # Calculate style gram matrices
        style_grams = {layer: self.gram_matrix(style_features[layer]) 
                       for layer in self.style_layers}
        
        # Optimizer
        optimizer = optim.LBFGS([input_img.requires_grad_()])
        
        run = [0]
        
        def closure():
            # Correct the values of updated input image
            input_img.data.clamp_(0, 1)
            
            optimizer.zero_grad()
            
            # Get features of input image
            input_features = self.get_features(input_img, self.vgg)
            
            # Content loss
            content_loss = 0
            for layer in self.content_layers:
                content_loss += torch.mean((input_features[layer] - content_features[layer]) ** 2)
            content_loss *= content_weight
            
            # Style loss
            style_loss = 0
            for layer in self.style_layers:
                input_gram = self.gram_matrix(input_features[layer])
                style_gram = style_grams[layer]
                layer_style_loss = torch.mean((input_gram - style_gram) ** 2)
                style_loss += layer_style_loss
            style_loss *= style_weight
            
            # Total loss
            total_loss = content_loss + style_loss
            total_loss.backward()
            
            run[0] += 1
            
            if run[0] % 50 == 0:
                print(f"Step {run[0]}/{num_steps} - Content Loss: {content_loss.item():.2f}, Style Loss: {style_loss.item():.2f}")
                
                if callback:
                    progress = (run[0] / num_steps) * 100
                    callback(progress, run[0], num_steps)
            
            return total_loss
        
        # Optimization loop
        for step in range(num_steps):
            optimizer.step(closure)
            
            if run[0] >= num_steps:
                break
        
        # Final cleanup
        input_img.data.clamp_(0, 1)
        
        # Save result
        output_image = self.save_image(input_img, output_path)
        
        print(f"✅ Style transfer complete! Saved to {output_path}")
        
        return output_path
    
    def quick_transfer(self, content_path, style_path, output_path, intensity=1.0):
        """
        Faster style transfer with fewer iterations
        
        Args:
            intensity: Style strength (0.0 to 2.0)
        """
        num_steps = 150  # Fewer steps for speed
        style_weight = int(1000000 * intensity)
        
        return self.transfer_style(
            content_path, 
            style_path, 
            output_path,
            num_steps=num_steps,
            style_weight=style_weight,
            content_weight=1
        )