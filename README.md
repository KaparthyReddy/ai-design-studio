# AI Design Studio 🎨

An AI-powered design studio using GANs for artistic style transfer and generative design. Transform your images across multiple artistic styles with the power of deep learning.

## Features

- 🖼️ **Neural Style Transfer**: Apply artistic styles to any image
- 🎭 **Multiple Style Presets**: Choose from various pre-trained artistic styles
- 🎚️ **Style Intensity Control**: Fine-tune the strength of style application
- 🔄 **Style Mixing**: Blend multiple styles together
- 📊 **Real-time Preview**: See results as you adjust parameters
- 💾 **Gallery Management**: Save and manage your creations
- ⚡ **Apple Silicon Optimized**: Leverages M4's Metal Performance Shaders

## Tech Stack

**Backend:**
- Python 3.10+
- Flask (REST API)
- PyTorch (with MPS support for M4)
- OpenCV, Pillow

**Frontend:**
- React 18
- Axios
- Modern CSS3

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- macOS with Apple Silicon (M4)

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Backend runs on `http://localhost:5000`

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

## Project Structure
```
ai-design-studio/
├── backend/          # Flask API and ML models
├── frontend/         # React application
├── notebooks/        # Jupyter notebooks for experiments
└── docs/            # Documentation
```

## API Endpoints

- `POST /api/transfer` - Apply style transfer to an image
- `GET /api/styles` - Get available style presets
- `GET /api/gallery` - Retrieve saved images
- `POST /api/upload` - Upload new image

## Development Timeline

- **Day 1**: Setup, model implementation, basic backend
- **Day 2**: Advanced GAN features, model optimization
- **Day 3**: Frontend development, integration, testing

## License

MIT License