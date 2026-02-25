// Upload handlers for image and video

// Image Upload
if (document.getElementById('image-form')) {
    const imageForm = document.getElementById('image-form');
    const imageInput = document.getElementById('image-input');
    const previewSection = document.getElementById('preview-section');
    const previewImage = document.getElementById('preview-image');
    const resultsSection = document.getElementById('results-section');
    const loading = document.getElementById('loading');
    const resultsContent = document.getElementById('results-content');
    
    // Show file name
    imageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            document.getElementById('file-name').textContent = file.name;
            
            // Show preview
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewSection.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Handle form submission
    imageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const file = imageInput.files[0];
        if (!file) return;
        
        // Show loading
        resultsSection.style.display = 'block';
        loading.style.display = 'block';
        resultsContent.style.display = 'none';
        
        try {
            // Prepare form data
            const formData = new FormData();
            formData.append('file', file);
            
            // Send request
            const response = await fetch('/api/detect/image', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Upload failed');
            }
            
            const data = await response.json();
            
            // Hide loading, show results
            loading.style.display = 'none';
            resultsContent.style.display = 'block';
            
            // Display annotated image
            document.getElementById('result-image').src = data.annotated_image_url;
            
            // Update summary
            document.getElementById('total-faces').textContent = data.summary.total_faces;
            document.getElementById('mask-on-count').textContent = data.summary.label_counts.MASK_ON || 0;
            document.getElementById('no-mask-count').textContent = data.summary.label_counts.NO_MASK || 0;
            document.getElementById('incorrect-count').textContent = data.summary.label_counts.MASK_INCORRECT || 0;
            
            // Populate detections table
            const tbody = document.getElementById('detections-tbody');
            tbody.innerHTML = data.detections.map((det, idx) => `
                <tr>
                    <td>${idx + 1}</td>
                    <td><span class="badge badge-${det.label.toLowerCase().replace('_', '-')}">${det.label}</span></td>
                    <td>${(det.confidence * 100).toFixed(1)}%</td>
                    <td>[${det.box.join(', ')}]</td>
                </tr>
            `).join('');
            
        } catch (error) {
            alert('Error processing image: ' + error.message);
            console.error('Error:', error);
            loading.style.display = 'none';
        }
    });
}

// Video Upload
if (document.getElementById('video-form')) {
    const videoForm = document.getElementById('video-form');
    const videoInput = document.getElementById('video-input');
    const progressSection = document.getElementById('progress-section');
    const resultsSection = document.getElementById('results-section');
    const uploadStatus = document.getElementById('upload-status');
    
    let currentJobId = null;
    let pollInterval = null;
    
    // Show file name
    videoInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const sizeMB = (file.size / 1024 / 1024).toFixed(1);
            document.getElementById('file-name').textContent = `${file.name} (${sizeMB} MB)`;
        }
    });
    
    // Handle form submission
    videoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const file = videoInput.files[0];
        if (!file) return;
        
        // Check file size
        if (file.size > 50 * 1024 * 1024) {
            alert('Video file is too large. Maximum size is 50MB.');
            return;
        }
        
        try {
            // Show uploading status
            uploadStatus.style.display = 'block';
            uploadStatus.className = 'status-message status-info';
            uploadStatus.textContent = 'Uploading video...';
            
            // Prepare form data
            const formData = new FormData();
            formData.append('file', file);
            
            // Send request
            const response = await fetch('/api/jobs/video', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Upload failed');
            }
            
            const data = await response.json();
            currentJobId = data.job_id;
            
            // Show progress section
            uploadStatus.style.display = 'none';
            progressSection.style.display = 'block';
            resultsSection.style.display = 'none';
            
            document.getElementById('job-id').textContent = currentJobId;
            
            // Start polling for status
            startPolling();
            
        } catch (error) {
            uploadStatus.className = 'status-message status-error';
            uploadStatus.textContent = 'Error: ' + error.message;
            console.error('Error:', error);
        }
    });
    
    function startPolling() {
        pollInterval = setInterval(checkJobStatus, 2000);
    }
    
    function stopPolling() {
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
    }
    
    async function checkJobStatus() {
        try {
            const response = await fetch(`/api/jobs/video/${currentJobId}`);
            if (!response.ok) {
                throw new Error('Failed to get job status');
            }
            
            const data = await response.json();
            
            // Update progress
            document.getElementById('progress-fill').style.width = data.progress + '%';
            document.getElementById('progress-percent').textContent = data.progress + '%';
            document.getElementById('job-status').textContent = data.status;
            
            if (data.status === 'processing') {
                document.getElementById('progress-status').textContent = 'Processing frames...';
            } else if (data.status === 'completed') {
                stopPolling();
                showResults(data);
            } else if (data.status === 'failed') {
                stopPolling();
                document.getElementById('progress-status').textContent = 'Failed: ' + data.error;
            }
            
        } catch (error) {
            console.error('Polling error:', error);
        }
    }
    
    function showResults(data) {
        progressSection.style.display = 'none';
        resultsSection.style.display = 'block';
        
        // Set download link
        document.getElementById('download-link').href = data.output_video_url;
        
        // Update summary
        document.getElementById('total-frames').textContent = data.summary.total_frames;
        document.getElementById('processed-frames').textContent = data.summary.processed_frames;
        document.getElementById('total-detections').textContent = data.summary.total_detections;
        
        // Update distribution bars
        const labelCounts = data.summary.label_counts;
        const total = data.summary.total_detections || 1;
        
        const maskOnCount = labelCounts.MASK_ON || 0;
        const noMaskCount = labelCounts.NO_MASK || 0;
        const incorrectCount = labelCounts.MASK_INCORRECT || 0;
        
        document.getElementById('bar-mask-on').style.width = ((maskOnCount / total) * 100) + '%';
        document.getElementById('bar-no-mask').style.width = ((noMaskCount / total) * 100) + '%';
        document.getElementById('bar-incorrect').style.width = ((incorrectCount / total) * 100) + '%';
        
        document.getElementById('count-mask-on').textContent = maskOnCount;
        document.getElementById('count-no-mask').textContent = noMaskCount;
        document.getElementById('count-incorrect').textContent = incorrectCount;
    }
    
    // Process another video
    document.getElementById('process-another-btn')?.addEventListener('click', () => {
        resultsSection.style.display = 'none';
        progressSection.style.display = 'none';
        videoForm.reset();
        document.getElementById('file-name').textContent = 'Click to select video (max 50MB)';
    });
}
