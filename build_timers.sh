#!/bin/bash

# Script to build standalone TimerApp with PyInstaller
# Usage: ./build_timers.sh

set -e

echo "🚀 Building Standalone TimerApp..."
echo "================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check for PyInstaller
print_status "Checking for PyInstaller..."
PYINSTALLER_PATH=""
if command -v pyinstaller &> /dev/null; then
    PYINSTALLER_PATH="pyinstaller"
    print_success "PyInstaller found"
elif [ -f "/Users/haonguyen/Library/Python/3.9/bin/pyinstaller" ]; then
    PYINSTALLER_PATH="/Users/haonguyen/Library/Python/3.9/bin/pyinstaller"
    print_success "PyInstaller found (user install)"
elif python3 -m PyInstaller --version &> /dev/null; then
    PYINSTALLER_PATH="python3 -m PyInstaller"
    print_success "PyInstaller found (module)"
else
    print_error "PyInstaller not found"
    echo "💡 Install: pip3 install pyinstaller"
    exit 1
fi

# Check for main Python file
if [ ! -f "timers.py" ]; then
    print_error "timers.py not found"
    exit 1
fi

# Clean previous build
print_status "Cleaning previous build..."
rm -rf build/ dist/ TimerApp.app
print_success "Cleaned up"

# Build with PyInstaller
print_status "Building standalone app with PyInstaller..."
echo "⏳ This may take a few minutes..."

$PYINSTALLER_PATH --noconfirm --onedir --windowed \
  --icon=icon64.png \
  --add-data "alert.mp3:." \
  --add-data "icon64.png:." \
  --name TimerApp \
  --osx-bundle-identifier com.yourcompany.timerapp \
  --target-arch universal2 \
  timers.py

# Copy Info.plist to bundle
print_status "Copying Info.plist to bundle..."
cp Info.plist dist/TimerApp.app/Contents/Info.plist
print_success "Info.plist copied"

# Check if app was created
if [ -d "dist/TimerApp.app" ]; then
    print_success "Standalone app created"
    
    # Copy app to root
    cp -r dist/TimerApp.app .
    print_success "App copied to project root"
    
    # Set executable permissions
    chmod +x TimerApp.app/Contents/MacOS/TimerApp
    print_success "Executable permissions set"
    
    # Display info
    echo ""
    print_success "🎉 Standalone TimerApp ready!"
    echo ""
    echo "📱 App info:"
    echo "   • Name: TimerApp.app"
    echo "   • Size: $(du -sh TimerApp.app | cut -f1)"
    echo "   • Location: $(pwd)/TimerApp.app"
    echo ""
    echo "🚀 Usage:"
    echo "   • Copy TimerApp.app to /Applications/"
    echo "   • Right-click > Open to bypass Gatekeeper"
    echo "   • Or: open TimerApp.app from Terminal"
    echo ""
    echo "⚠ Warning:"
    echo "   • App not codesigned/notarized, may be blocked by Gatekeeper"
    echo "   • On other Macs, use: open /Applications/TimerApp.app"
    echo "   • Or allow app in System Settings > Privacy & Security"
    echo ""
    echo "✨ Standalone features:"
    echo "   • No Python installation needed"
    echo "   • No dependencies required"
    echo "   • Runs on macOS 10.15+"
    echo "   • Universal binary (Intel & Apple Silicon)"
else
    print_error "Standalone app not created"
    exit 1
fi

# Clean up temporary files
print_status "Cleaning up temporary files..."
rm -rf build/ dist/
print_success "Cleaned up"

echo ""
print_success "✅ Done! Standalone app ready to share."