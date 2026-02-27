#!/bin/bash

# MaskGuard Railway Deployment Script
# This script automates the deployment to Railway

set -e

echo "🚀 MaskGuard Railway Deployment"
echo "================================"
echo ""

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📥 Installing Railway CLI..."
    npm install -g @railway/cli
fi

echo "✓ Railway CLI ready"
echo ""

# Check if logged in
if ! railway whoami &> /dev/null 2>&1; then
    echo "🔐 Need to authenticate with Railway"
    echo ""
    echo "📱 Railway login will open in your browser"
    echo "Steps:"
    echo "  1. Click 'Authorize with GitHub'"
    echo "  2. Authorize railway app access"
    echo "  3. Return to terminal"
    echo ""
    echo "Press Enter to continue..."
    read
    
    railway login || {
        echo "❌ Railway login failed"
        exit 1
    }
fi

echo "✓ Authenticated with Railway"
echo ""

# Navigate to project directory
cd /workspaces/Mask-Detector

# Check if already initialized
if [ ! -f ".railway/config.json" ]; then
    echo "📦 Initializing Railway project..."
    railway init --name maskguard || {
        echo "❌ Railway initialization failed"
        exit 1
    }
    echo "✓ Project initialized"
else
    echo "✓ Project already initialized"
fi

echo ""
echo "🔨 Building and deploying to Railway..."
echo ""

# Deploy
railway up --detach || {
    echo "❌ Deployment failed"
    exit 1
}

echo ""
echo "✅ Deployment successful!"
echo ""

# Get project details
echo "📊 Project Details:"
PROJECT_ID=$(railway config --json 2>/dev/null | grep -o '"projectId":"[^"]*' | cut -d'"' -f4)
if [ ! -z "$PROJECT_ID" ]; then
    echo "  Project ID: $PROJECT_ID"
fi

echo ""
echo "📝 Next steps:"
echo "  1. View your live app: railway open"
echo "  2. Stream logs: railway logs --follow"
echo "  3. Set variables: railway dashboard"
echo "  4. Check status: railway status"
echo ""

# Provide the URL
echo "🌐 Getting your deployment URL..."
sleep 3

if railway open &> /dev/null; then
    echo "✓ Opening Railway dashboard..."
fi

echo ""
echo "✨ Deployment complete!"
echo ""
echo "Your app is live on Railway! 🎉"
echo ""
echo "📚 Documentation: https://docs.railway.app/"
echo "💬 Discord: https://railway.app/discord"
