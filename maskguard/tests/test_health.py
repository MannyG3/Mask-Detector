import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data

def test_home_page():
    """Test the home page loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert "MaskGuard" in response.text

def test_live_page():
    """Test the live detection page loads."""
    response = client.get("/live")
    assert response.status_code == 200

def test_upload_image_page():
    """Test the upload image page loads."""
    response = client.get("/upload/image")
    assert response.status_code == 200

def test_upload_video_page():
    """Test the upload video page loads."""
    response = client.get("/upload/video")
    assert response.status_code == 200

def test_dashboard_page():
    """Test the dashboard page loads."""
    response = client.get("/dashboard")
    assert response.status_code == 200

def test_stats_endpoint():
    """Test the stats API endpoint."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "by_label" in data
    assert "by_source" in data

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
