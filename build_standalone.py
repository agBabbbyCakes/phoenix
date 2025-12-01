#!/usr/bin/env python3
"""
Build script for creating standalone executables for all platforms.
This script helps build for Windows, macOS, Linux, and Raspberry Pi.
"""
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller."""
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_for_platform(platform_name, spec_file):
    """Build executable for a specific platform."""
    print(f"\n{'='*60}")
    print(f"Building for {platform_name}")
    print(f"{'='*60}")
    
    if not Path(spec_file).exists():
        print(f"❌ Spec file not found: {spec_file}")
        return False
    
    try:
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", spec_file]
        subprocess.check_call(cmd)
        print(f"✅ Build successful for {platform_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed for {platform_name}: {e}")
        return False

def main():
    """Main build function."""
    print("Phoenix Dashboard - Standalone Build Script")
    print("=" * 60)
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("PyInstaller not found. Installing...")
        install_pyinstaller()
    
    # Detect current platform
    current_platform = platform.system().lower()
    print(f"Current platform: {current_platform}")
    
    # Create downloads directory
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    # Build for current platform
    if current_platform == "windows":
        spec_file = "phoenix_windows.spec"
        output_name = "PhoenixDashboard.exe"
    elif current_platform == "darwin":
        spec_file = "phoenix_macos.spec"
        output_name = "PhoenixDashboard"
    else:  # Linux
        spec_file = "phoenix_linux.spec"
        output_name = "PhoenixDashboard"
    
    if Path(spec_file).exists():
        success = build_for_platform(current_platform, spec_file)
        if success:
            # Copy to downloads
            dist_dir = Path("dist")
            if dist_dir.exists():
                exe_path = dist_dir / output_name
                if exe_path.exists():
                    dest = downloads_dir / f"PhoenixDashboard-{current_platform}-{platform.machine()}"
                    if current_platform == "windows":
                        dest = dest.with_suffix(".exe")
                    shutil.copy2(exe_path, dest)
                    print(f"\n✅ Executable copied to: {dest}")
    else:
        print(f"⚠️  Platform-specific spec file not found: {spec_file}")
        print("   Using generic spec file...")
        if Path("phoenix.spec").exists():
            build_for_platform(current_platform, "phoenix.spec")
    
    print("\n" + "=" * 60)
    print("Build process complete!")
    print("=" * 60)
    print("\nNote: To build for other platforms, run this script on those platforms,")
    print("      or use cross-compilation tools.")

if __name__ == "__main__":
    main()


