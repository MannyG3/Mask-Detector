// Live Mask Detection with WebSocket

class LiveDetection {
    constructor() {
        this.ws = null;
        this.video = document.getElementById('webcam');
        this.canvas = document.getElementById('overlay');
        this.ctx = this.canvas.getContext('2d');
        this.stream = null;
        this.isRunning = false;
        this.frameInterval = null;
        
        // Settings
        this.confidenceThreshold = 0.5;
        this.fpsCap = 5;
        this.enableSound = true;
        this.enableSnapshots = false;
        this.cooldownSeconds = 10;
        
        // Stats
        this.facesCount = 0;
        this.violationsCount = 0;
        this.lastFrameTime = Date.now();
        this.fps = 0;
        
        // Audio context for beep
        this.audioContext = null;
        
        // Detection log
        this.recentDetections = [];
        this.maxLogEntries = 10;
        
        this.initializeElements();
        this.attachEventListeners();
        this.loadInitialSettings();
    }
    
    initializeElements() {
        this.startBtn = document.getElementById('start-btn');
        this.stopBtn = document.getElementById('stop-btn');
        this.statusChip = document.getElementById('status-chip');
        this.statusText = document.getElementById('status-text');
        this.facesCountEl = document.getElementById('faces-count');
        this.violationsCountEl = document.getElementById('violations-count');
        this.fpsDisplay = document.getElementById('fps-display');
        this.detectionsListEl = document.getElementById('detections-list');
    }
    
    attachEventListeners() {
        this.startBtn.addEventListener('click', () => this.start());
        this.stopBtn.addEventListener('click', () => this.stop());
        
        // Settings
        document.getElementById('confidence-threshold').addEventListener('input', (e) => {
            this.confidenceThreshold = parseFloat(e.target.value);
            document.getElementById('threshold-value').textContent = this.confidenceThreshold;
        });
        
        document.getElementById('fps-cap').addEventListener('change', (e) => {
            this.fpsCap = parseInt(e.target.value);
            document.getElementById('fps-value').textContent = this.fpsCap;
            if (this.isRunning) {
                this.restartFrameCapture();
            }
        });
        
        document.getElementById('enable-snapshots').addEventListener('change', (e) => {
            this.enableSnapshots = e.target.checked;
            this.sendConfig();
        });
        
        document.getElementById('enable-sound').addEventListener('change', (e) => {
            this.enableSound = e.target.checked;
            if (this.enableSound && !this.audioContext) {
                this.initAudio();
            }
        });

        document.getElementById('cooldown-seconds').addEventListener('change', (e) => {
            const value = parseInt(e.target.value, 10);
            if (!Number.isNaN(value)) {
                this.cooldownSeconds = value;
                document.getElementById('cooldown-value').textContent = value;
                this.sendConfig();
            }
        });
    }

    loadInitialSettings() {
        const snapshotsEl = document.getElementById('enable-snapshots');
        if (snapshotsEl) {
            this.enableSnapshots = snapshotsEl.checked;
        }
        const soundEl = document.getElementById('enable-sound');
        if (soundEl) {
            this.enableSound = soundEl.checked;
        }
        const cooldownEl = document.getElementById('cooldown-seconds');
        if (cooldownEl) {
            const value = parseInt(cooldownEl.value, 10);
            if (!Number.isNaN(value)) {
                this.cooldownSeconds = value;
            }
        }
    }

    sendConfig() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'config',
                cooldown_seconds: this.cooldownSeconds,
                snapshots_enabled: this.enableSnapshots
            }));
        }
    }
    
    initAudio() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
    }
    
    playBeep() {
        if (!this.enableSound || !this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.2);
    }
    
    async start() {
        try {
            // Get webcam stream
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 }
            });
            
            this.video.srcObject = this.stream;
            await this.video.play();
            
            // Set canvas size
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            
            // Connect WebSocket
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/live`;
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.isRunning = true;
                this.updateStatus('active', 'Active');
                this.startBtn.disabled = true;
                this.stopBtn.disabled = false;
                this.sendConfig();
                this.startFrameCapture();
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleDetectionResult(data);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.stop();
            };
            
            this.ws.onclose = () => {
                if (this.isRunning) {
                    this.stop();
                }
            };
            
        } catch (error) {
            alert('Failed to access webcam: ' + error.message);
            console.error('Camera error:', error);
        }
    }
    
    stop() {
        this.isRunning = false;
        
        // Stop frame capture
        if (this.frameInterval) {
            clearInterval(this.frameInterval);
            this.frameInterval = null;
        }
        
        // Close WebSocket
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        // Stop video stream
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Update UI
        this.updateStatus('inactive', 'Stopped');
        this.startBtn.disabled = false;
        this.stopBtn.disabled = true;
        this.facesCount = 0;
        this.violationsCount = 0;
        this.updateStats();
    }
    
    startFrameCapture() {
        const interval = 1000 / this.fpsCap;
        this.frameInterval = setInterval(() => {
            this.captureAndSendFrame();
        }, interval);
    }
    
    restartFrameCapture() {
        if (this.frameInterval) {
            clearInterval(this.frameInterval);
        }
        this.startFrameCapture();
    }
    
    captureAndSendFrame() {
        if (!this.isRunning || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }
        
        // Draw video frame to temporary canvas
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = this.video.videoWidth;
        tempCanvas.height = this.video.videoHeight;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.drawImage(this.video, 0, 0);
        
        // Convert to JPEG and send
        const dataUrl = tempCanvas.toDataURL('image/jpeg', 0.8);
        
        this.ws.send(JSON.stringify({
            type: 'frame',
            data: dataUrl
        }));
        
        // Calculate FPS
        const now = Date.now();
        const delta = now - this.lastFrameTime;
        this.fps = Math.round(1000 / delta);
        this.lastFrameTime = now;
        this.updateStats();
    }
    
    handleDetectionResult(data) {
        const { detections, alert, faces_count } = data;
        
        // Update stats
        this.facesCount = faces_count || 0;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw detections
        let hasViolations = false;
        detections.forEach(detection => {
            const { box, label, confidence, track_id, alert: shouldAlert } = detection;
            
            if (confidence < this.confidenceThreshold) return;
            
            const [x1, y1, x2, y2] = box;
            
            // Determine color
            let color = '#00ff00';  // Green for MASK_ON
            if (label === 'NO_MASK' || label === 'MASK_INCORRECT') {
                color = '#ff0000';  // Red for violations
                hasViolations = true;
            }
            
            // Draw box
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 3;
            this.ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
            
            // Draw label background
            const labelText = `${label} (${(confidence * 100).toFixed(0)}%)`;
            this.ctx.font = '16px Arial';
            const textWidth = this.ctx.measureText(labelText).width;
            
            this.ctx.fillStyle = color;
            this.ctx.fillRect(x1, y1 - 25, textWidth + 10, 25);
            
            // Draw label text
            this.ctx.fillStyle = '#ffffff';
            this.ctx.fillText(labelText, x1 + 5, y1 - 7);
            
            // Draw track ID
            if (track_id) {
                this.ctx.fillStyle = color;
                this.ctx.font = '12px Arial';
                this.ctx.fillText(track_id, x1, y2 + 15);
            }
            
            // Add to recent detections log
            if (shouldAlert) {
                this.addDetectionToLog(label, confidence, track_id);
            }
        });
        
        // Update violations count
        if (hasViolations) {
            this.violationsCount++;
        }
        
        // Play alert sound
        if (alert && hasViolations) {
            this.playBeep();
        }
        
        this.updateStats();
    }
    
    addDetectionToLog(label, confidence, trackId) {
        const timestamp = new Date().toLocaleTimeString();
        this.recentDetections.unshift({
            timestamp,
            label,
            confidence,
            trackId
        });
        
        // Keep only recent entries
        if (this.recentDetections.length > this.maxLogEntries) {
            this.recentDetections.pop();
        }
        
        this.updateDetectionsList();
    }
    
    updateDetectionsList() {
        this.detectionsListEl.innerHTML = this.recentDetections.map(d => `
            <div class="log-entry ${d.label.toLowerCase().replace('_', '-')}">
                <span class="log-time">${d.timestamp}</span>
                <span class="log-label">${d.label}</span>
                <span class="log-confidence">${(d.confidence * 100).toFixed(0)}%</span>
                ${d.trackId ? `<span class="log-track">${d.trackId}</span>` : ''}
            </div>
        `).join('');
    }
    
    updateStats() {
        this.facesCountEl.textContent = this.facesCount;
        this.violationsCountEl.textContent = this.violationsCount;
        this.fpsDisplay.textContent = this.fps;
    }
    
    updateStatus(state, text) {
        this.statusChip.className = `status-chip status-${state}`;
        this.statusText.textContent = text;
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new LiveDetection();
});
