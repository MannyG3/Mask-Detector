#!/bin/bash

# MaskGuard API Integration Tests
echo "========================================"
echo "MaskGuard API Integration Tests"
echo "========================================"
echo ""

BASE_URL="http://localhost:8000"

# Test 1: Health Check
echo "✓ Test 1: Health Check"
curl -s "$BASE_URL/api/health" | jq '.'
echo ""

# Test 2: Homepage
echo "✓ Test 2: Homepage"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ "$STATUS" = "200" ]; then
    echo "Homepage: OK ($STATUS)"
else
    echo "Homepage: FAILED ($STATUS)"
fi
echo ""

# Test 3: Live Detection Page
echo "✓ Test 3: Live Detection Page"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/live")
if [ "$STATUS" = "200" ]; then
    echo "Live Page: OK ($STATUS)"
else
    echo "Live Page: FAILED ($STATUS)"
fi
echo ""

# Test 4: Image Upload Page
echo "✓ Test 4: Image Upload Page"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/upload/image")
if [ "$STATUS" = "200" ]; then
    echo "Image Upload Page: OK ($STATUS)"
else
    echo "Image Upload Page: FAILED ($STATUS)"
fi
echo ""

# Test 5: Video Upload Page
echo "✓ Test 5: Video Upload Page"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/upload/video")
if [ "$STATUS" = "200" ]; then
    echo "Video Upload Page: OK ($STATUS)"
else
    echo "Video Upload Page: FAILED ($STATUS)"
fi
echo ""

# Test 6: Dashboard Page
echo "✓ Test 6: Dashboard"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/dashboard")
if [ "$STATUS" = "200" ]; then
    echo "Dashboard: OK ($STATUS)"
else
    echo "Dashboard: FAILED ($STATUS)"
fi
echo ""

# Test 7: CSV Export
echo "✓ Test 7: CSV Export"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/logs/export.csv")
if [ "$STATUS" = "200" ]; then
    echo "CSV Export: OK ($STATUS)"
else
    echo "CSV Export: FAILED ($STATUS)"
fi
echo ""

# Test 8: Static CSS
echo "✓ Test 8: Static CSS"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/static/css/app.css")
if [ "$STATUS" = "200" ]; then
    echo "CSS File: OK ($STATUS)"
else
    echo "CSS File: FAILED ($STATUS)"
fi
echo ""

# Test 9: Static JS
echo "✓ Test 9: Static JS Files"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/static/js/live.js")
if [ "$STATUS" = "200" ]; then
    echo "live.js: OK ($STATUS)"
else
    echo "live.js: FAILED ($STATUS)"
fi
echo ""

# Test 10: Create Test Image
echo "✓ Test 10: Image Detection Endpoint"
TEST_IMG="/tmp/test.jpg"
convert -size 400x300 xc:blue -fill white -pointsize 30 -annotate +50+150 'TEST' "$TEST_IMG" 2>/dev/null || {
    # Fallback: create simple test image with Python
    python3 -c "
import cv2
import numpy as np
img = np.zeros((300, 400, 3), dtype=np.uint8)
img[:] = (255, 100, 100)
cv2.imwrite('$TEST_IMG', img)
" 2>/dev/null
}

if [ -f "$TEST_IMG" ]; then
    RESULT=$(curl -s -F "file=@$TEST_IMG" "$BASE_URL/api/detect/image")
    if echo "$RESULT" | jq -e '.detection_result' > /dev/null 2>&1; then
        echo "Image Detection: OK"
        echo "$RESULT" | jq -r '.detection_result' | head -3
    else
        echo "Image Detection: FAILED"
        echo "$RESULT"
    fi
    rm -f "$TEST_IMG"
else
    echo "Image Detection: SKIPPED (could not create test image)"
fi
echo ""

echo "========================================"
echo "All Tests Complete!"
echo "========================================"
