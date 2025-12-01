"""
Version and build number management for Phoenix Dashboard.
Generates build numbers and timestamps for standalone applications.
"""
import os
from datetime import datetime, timezone
from pathlib import Path

VERSION_FILE = Path(__file__).parent / "VERSION"
BUILD_INFO_FILE = Path(__file__).parent / "BUILD_INFO.txt"

def get_version():
    """Get current version from VERSION file or default."""
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text().strip()
    return "0.1.0"

def get_build_number():
    """Get or create build number."""
    build_file = Path(__file__).parent / ".build_number"
    if build_file.exists():
        try:
            build_num = int(build_file.read_text().strip())
        except ValueError:
            build_num = 0
    else:
        build_num = 0
    
    # Increment build number
    build_num += 1
    build_file.write_text(str(build_num))
    
    return build_num

def get_build_timestamp():
    """Get current build timestamp."""
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

def get_build_info():
    """Get complete build information."""
    version = get_version()
    build_num = get_build_number()
    timestamp = get_build_timestamp()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    return {
        "version": version,
        "build_number": build_num,
        "build_timestamp": timestamp,
        "build_date": date_str,
        "version_string": f"{version}.{build_num}",
        "full_version": f"{version}.{build_num}.{timestamp}"
    }

def write_build_info():
    """Write build info to BUILD_INFO.txt."""
    info = get_build_info()
    content = f"""Phoenix Dashboard - Build Information
=====================================
Version: {info['version']}
Build Number: {info['build_number']}
Build Timestamp: {info['build_timestamp']}
Build Date: {info['build_date']}
Version String: {info['version_string']}
Full Version: {info['full_version']}
"""
    BUILD_INFO_FILE.write_text(content)
    return info

if __name__ == "__main__":
    info = write_build_info()
    print(f"Version: {info['version_string']}")
    print(f"Build: {info['build_number']}")
    print(f"Timestamp: {info['build_timestamp']}")
    print(f"Full: {info['full_version']}")

