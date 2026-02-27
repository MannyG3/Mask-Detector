# 🛡️ MaskGuard - Advanced Mask Detection System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Railway-blueviolet.svg)](https://maskdetector.up.railway.app)

**🚀 Live Demo: [https://maskdetector.up.railway.app](https://maskdetector.up.railway.app)**

A production-ready web application for real-time mask detection with live webcam monitoring, image upload analysis, and video processing. Built with FastAPI, MediaPipe, and TensorFlow.

## ✨ Features

### 🎯 Detection Capabilities
- **3-Class Detection**: MASK_ON, NO_MASK, MASK_INCORRECT (mask below nose)
- **MediaPipe Face Detection**: Robust face detection in various conditions
- **Face Tracking**: Centroid-based tracking to reduce flicker and enable smart alerts
- **Cooldown Alerts**: Prevent alert spam with configurable cooldown periods

### 📹 Live Webcam Monitoring
- Real-time webcam stream processing with WebRTC
- Canvas overlay with bounding boxes and labels
- Configurable FPS cap (3/5/10/15 FPS)
- Sound alerts for violations (Web Audio API)
- Live statistics: face count, violations, FPS

### 🖼️ Image Upload
- Upload images for instant analysis
- Annotated output with bounding boxes
- Detection summary and detailed results table
- Automatic logging to database

### 🎥 Video Processing
- Async video processing with progress tracking
- Frame-by-frame analysis with configurable sampling rate
- Annotated output video generation
- Detection statistics and distribution charts

### 📊 Dashboard
- Event logs with filtering (source, label, date range)
- Statistics cards (total events, label distribution)
- CSV export for compliance reports
- Real-time stats updates

### 🔧 Advanced Features
- **Dummy Model Mode**: Run without a trained model for testing/demo
- **SQLite Logging**: All detections logged with metadata
- **Snapshot Capture**: Optional screenshot saves for violations
- **Production-Ready**: Dockerized, deployable to Render/Railway/Fly.io

## 🏗️ Architecture

```
maskguard/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── db.py                   # Database operations
│   ├── models/
│   │   ├── face_detector.py    # MediaPipe face detection
│   │   ├── classifier.py       # Mask classification (with dummy mode)
│   │   └── tracker.py          # Centroid tracking
│   ├── services/
│   │   ├── logger.py           # Event logging with cooldown
│   │   ├── video_worker.py     # Background video processing
│   │   └── storage.py          # File upload/storage management
│   ├── routes/
│   │   ├── api.py              # REST API endpoints
│   │   ├── ws.py               # WebSocket endpoint
│   │   └── pages.py            # Page routes
│   ├── templates/              # Jinja2 HTML templates
│   └── static/
│       ├── css/app.css         # Styling
│       └── js/                 # Frontend JavaScript
├── data/                       # Runtime data (created automatically)
│   ├── logs/                   # SQLite database
│   ├── uploads/                # Uploaded files
│   ├── outputs/                # Processed outputs
│   └── captures/               # Violation snapshots
├── tests/
│   └── test_health.py          # Unit tests
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Local Development (Codespaces/Local Machine)

1. **Navigate to project directory**
```bash
cd maskguard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (optional)
```bash
cp .env.example .env
# Edit .env if needed
```

4. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Open in browser**
```
http://localhost:8000
```

### Docker Deployment

1. **Build the image**
```bash
docker build -t maskguard .
```

2. **Run the container**
```bash
docker run -p 8000:8000 -e DUMMY_MODEL=true maskguard
```

## 🌐 Deployment

### Deploy to Render

1. **Create a new Web Service** on [Render](https://render.com)

2. **Connect your GitHub repository**

3. **Configure the service**:
   - **Environment**: Docker
   - **Root Directory**: `maskguard`
   - **Docker Build Context**: `maskguard`

4. **Add environment variables**:
   ```
   DUMMY_MODEL=true
   ALERT_COOLDOWN_SECONDS=10
   MAX_VIDEO_MB=50
   ```

5. **Deploy!** Render will automatically build and deploy your app.

### Deploy to Railway

1. **Install Railway CLI** or use the web dashboard

2. **Initialize project**:
```bash
railway init
```

3. **Set environment variables**:
```bash
railway variables set DUMMY_MODEL=true
railway variables set PORT=8000
```

4. **Deploy**:
```bash
railway up
```

### Deploy to Fly.io

1. **Install Fly CLI**:
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Login and launch**:
```bash
fly auth login
cd maskguard
fly launch
```

3. **Set environment variables**:
```bash
fly secrets set DUMMY_MODEL=true
```

4. **Deploy**:
```bash
fly deploy
```

### Deploy to Vercel (limited mode)

> ⚠️ Vercel runs this app in serverless mode, so WebSocket live detection and long video processing are limited.

1. Import the GitHub repository in Vercel
2. Set **Root Directory** to `maskguard`
3. Add environment variables:
   ```
   DUMMY_MODEL=true
   ALERT_COOLDOWN_SECONDS=10
   SNAPSHOTS_ENABLED=false
   DB_PATH=/tmp/events.db
   UPLOADS_DIR=/tmp/uploads
   OUTPUTS_DIR=/tmp/outputs
   CAPTURES_DIR=/tmp/captures
   ```
4. Deploy

For full step-by-step instructions, see `DEPLOYMENT.md`.

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DUMMY_MODEL` | `true` | Use simulated predictions (no model file needed) |
| `MODEL_PATH` | `models/mask_detection_model.h5` | Path to Keras model file |
| `ALERT_COOLDOWN_SECONDS` | `10` | Seconds between alerts for same track |
| `SNAPSHOTS_ENABLED` | `false` | Save snapshots for violations |
| `MAX_VIDEO_MB` | `50` | Maximum video upload size |
| `MAX_IMAGE_MB` | `10` | Maximum image upload size |
| `LIVE_FPS_CAP` | `5` | Default FPS for live detection |
| `VIDEO_PROCESS_FPS` | `5` | FPS for video processing |
| `PORT` | `8000` | Server port |

### Using a Real Model

1. **Train or obtain a mask detection model** that outputs one of:
   - Single sigmoid output (mask vs no mask) - app will synthesize INCORRECT class
   - 3-class softmax output (MASK_ON, NO_MASK, MASK_INCORRECT)

2. **Save model as Keras .h5 file**:
```python
model.save('models/mask_detection_model.h5')
```

3. **Place model file** in `maskguard/models/mask_detection_model.h5`

4. **Set environment variable**:
```bash
DUMMY_MODEL=false
```

5. **Restart application** - it will automatically load the model

### Model Input Requirements
- Input shape: (224, 224, 3)
- Color space: RGB
- Normalization: [0, 1]
- Format: Keras/TensorFlow model

## 📖 API Documentation

Once running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET | `/live` | Live webcam detection |
| GET | `/upload/image` | Image upload page |
| GET | `/upload/video` | Video upload page |
| GET | `/dashboard` | Dashboard with logs |
| GET | `/api/health` | Health check |
| POST | `/api/detect/image` | Detect masks in image |
| POST | `/api/jobs/video` | Create video processing job |
| GET | `/api/jobs/video/{id}` | Get job status |
| GET | `/api/logs/export.csv` | Export logs as CSV |
| WS | `/ws/live` | WebSocket for live detection |

## 🧪 Testing

Run the test suite:
```bash
cd maskguard
pytest tests/ -v
```

Or run specific test:
```bash
python tests/test_health.py
```

## 🎯 Usage Examples

### Live Detection
1. Go to `/live` page
2. Click "Start Camera" and allow webcam access
3. Adjust settings:
   - Confidence threshold
   - FPS cap
   - Enable/disable sound alerts
   - Enable/disable snapshots
4. Watch real-time detection with overlays

### Image Upload
1. Go to `/upload/image` page
2. Select an image file
3. Click "Analyze Image"
4. View annotated results and detection details

### Video Processing
1. Go to `/upload/video` page
2. Select a video file (max 50MB)
3. Click "Process Video"
4. Monitor progress
5. Download annotated video when complete

### Dashboard
1. Go to `/dashboard` page
2. View statistics cards
3. Filter logs by source, label, or date
4. Export logs as CSV for reports

## 🛠️ Troubleshooting

### Webcam not working in live mode
- Ensure browser has camera permissions
- Use HTTPS or localhost (required for getUserMedia)
- Check if camera is already in use by another app

### Video upload fails
- Check file size (max 50MB by default)
- Ensure video format is supported (mp4, avi, mov)
- Increase `MAX_VIDEO_MB` if needed

### Model loading errors
- Verify model file exists at correct path
- Check TensorFlow version compatibility
- Try running in DUMMY_MODEL mode first

### Docker build issues
- Ensure sufficient memory allocated to Docker
- Check network connectivity for package downloads
- Review build logs for specific errors

### Jobs reset on server restart
- This is expected behavior for in-memory job queue
- In production, you can implement persistent job storage
- Document uploaded videos are preserved in `data/uploads/`

## 📊 Database Schema

### Events Table
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,              -- ISO timestamp
    source TEXT NOT NULL,          -- live, image, video
    label TEXT NOT NULL,           -- MASK_ON, NO_MASK, MASK_INCORRECT
    confidence REAL NOT NULL,      -- 0.0 to 1.0
    track_id TEXT,                 -- For live detections
    snapshot_path TEXT,            -- Optional snapshot path
    meta TEXT                      -- JSON metadata
);
```

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **MediaPipe** - Robust face detection
- **TensorFlow** - Deep learning framework
- **OpenCV** - Computer vision library

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📧 Support
                     
For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Live webcam detection with WebSocket
- Image and video upload processing
- Dashboard with logs and exports
- Docker deployment support
- Dummy model mode for testing

---

**Built with ❤️ for mask compliance monitoring**

csavas