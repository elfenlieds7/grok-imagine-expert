"""
Dropbox Path Configuration - Cross-Platform Support
Manages file paths for Dropbox storage across multiple dev boxes (macOS, Windows, Linux).

All paths are relative to Dropbox/grok-imagine-expert/
This ensures consistency across different dev boxes and operating systems.

Platform-specific Dropbox locations:
- macOS/Linux: ~/Dropbox
- Windows: C:\\Users\\{username}\\Dropbox (or custom location)
"""

import os
import sys
import platform
from pathlib import Path
from typing import Optional

# =================================================================
# Platform Detection
# =================================================================

PLATFORM = platform.system()  # 'Darwin' (macOS), 'Windows', 'Linux'

def get_dropbox_base_path() -> Path:
    """Get Dropbox base directory for current platform.

    Returns:
        Path to Dropbox directory

    Detection order:
    1. Environment variable DROPBOX_PATH (if set)
    2. Platform-specific default location
    3. Common alternative locations

    Raises:
        FileNotFoundError: If Dropbox directory cannot be found
    """
    # 1. Check environment variable (allows user override)
    env_path = os.getenv('DROPBOX_PATH')
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    # 2. Platform-specific defaults
    home = Path.home()

    if PLATFORM == 'Darwin':  # macOS
        default_paths = [
            home / "Dropbox",
            home / "Library" / "CloudStorage" / "Dropbox"  # New macOS location
        ]
    elif PLATFORM == 'Windows':
        default_paths = [
            home / "Dropbox",
            Path("C:/Dropbox"),  # Sometimes installed here
            Path("D:/Dropbox"),  # Alternative drive
        ]
    elif PLATFORM == 'Linux':
        default_paths = [
            home / "Dropbox",
            home / ".dropbox" / "Dropbox"
        ]
    else:
        # Unknown platform, try home directory
        default_paths = [home / "Dropbox"]

    # 3. Try each possible location
    for path in default_paths:
        if path.exists() and path.is_dir():
            return path

    # Not found - provide helpful error message
    raise FileNotFoundError(
        f"Dropbox directory not found on {PLATFORM}. Searched:\n" +
        "\n".join(f"  - {p}" for p in default_paths) +
        f"\n\nPlease set DROPBOX_PATH environment variable to your Dropbox location."
    )

# =================================================================
# Base Paths (Cross-Platform)
# =================================================================

try:
    # Dropbox root (absolute path on this machine)
    DROPBOX_BASE = get_dropbox_base_path()
    DROPBOX_ROOT = DROPBOX_BASE / "grok-imagine-expert"

    # Ensure base directory exists
    DROPBOX_ROOT.mkdir(parents=True, exist_ok=True)

    # Projects root
    PROJECTS_ROOT = DROPBOX_ROOT / "projects"
    PROJECTS_ROOT.mkdir(exist_ok=True)

    # Temp directory for downloads
    TEMP_ROOT = DROPBOX_ROOT / "temp"
    TEMP_ROOT.mkdir(exist_ok=True)

    DROPBOX_AVAILABLE = True
    DROPBOX_ERROR = None

except FileNotFoundError as e:
    # Dropbox not found - set placeholder paths but don't fail
    DROPBOX_BASE = None
    DROPBOX_ROOT = None
    PROJECTS_ROOT = None
    TEMP_ROOT = None
    DROPBOX_AVAILABLE = False
    DROPBOX_ERROR = str(e)

# =================================================================
# Path Generators (Cross-Platform)
# =================================================================

def _check_dropbox_available():
    """Raise error if Dropbox is not available."""
    if not DROPBOX_AVAILABLE:
        raise RuntimeError(
            f"Dropbox is not available on this system.\n{DROPBOX_ERROR}"
        )

def get_project_path(project_id: str) -> Path:
    """Get absolute path for a project directory.

    Args:
        project_id: Project UUID or slug

    Returns:
        Absolute path to project directory

    Example:
        macOS:   /Users/songym/Dropbox/grok-imagine-expert/projects/20250107-landscape
        Windows: C:\\Users\\songym\\Dropbox\\grok-imagine-expert\\projects\\20250107-landscape
    """
    _check_dropbox_available()
    project_dir = PROJECTS_ROOT / project_id
    project_dir.mkdir(exist_ok=True)
    return project_dir


def get_pass_path(project_id: str, pass_id: str) -> Path:
    """Get absolute path for a pass directory.

    Args:
        project_id: Project UUID or slug
        pass_id: Pass identifier (e.g., 'pass-001')

    Returns:
        Absolute path to pass directory
    """
    pass_dir = get_project_path(project_id) / "passes" / pass_id
    pass_dir.mkdir(parents=True, exist_ok=True)
    return pass_dir


def get_images_path(project_id: str, pass_id: str) -> Path:
    """Get absolute path for images directory in a pass."""
    images_dir = get_pass_path(project_id, pass_id) / "images"
    images_dir.mkdir(exist_ok=True)
    return images_dir


def get_videos_path(project_id: str, pass_id: str) -> Path:
    """Get absolute path for videos directory in a pass."""
    videos_dir = get_pass_path(project_id, pass_id) / "videos"
    videos_dir.mkdir(exist_ok=True)
    return videos_dir


def get_exports_path(project_id: str) -> Path:
    """Get absolute path for exports directory in a project."""
    exports_dir = get_project_path(project_id) / "exports"
    exports_dir.mkdir(exist_ok=True)
    return exports_dir


def get_node_file_path(
    project_id: str,
    pass_id: str,
    node_id: str,
    node_type: str,
    extension: str = "mp4"
) -> Path:
    """Get absolute path for a specific node's file.

    Args:
        project_id: Project UUID or slug
        pass_id: Pass identifier
        node_id: Node UUID
        node_type: 'image' or 'video'
        extension: File extension (without dot)

    Returns:
        Absolute path to node file

    Note:
        Returns Path object which works across platforms.
        Use str(path) if you need string representation.
    """
    if node_type == "image":
        base_dir = get_images_path(project_id, pass_id)
        prefix = "img"
        ext = "jpg" if extension == "mp4" else extension
    elif node_type == "video":
        base_dir = get_videos_path(project_id, pass_id)
        prefix = "vid"
        ext = extension
    else:
        raise ValueError(f"Invalid node_type: {node_type}. Must be 'image' or 'video'.")

    filename = f"{prefix}-{node_id}.{ext}"
    return base_dir / filename


def get_temp_download_path(filename: str) -> Path:
    """Get absolute path for a temporary download file."""
    _check_dropbox_available()
    downloads_dir = TEMP_ROOT / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    return downloads_dir / filename


# =================================================================
# Relative Path Conversion (for Database Storage)
# =================================================================
# IMPORTANT: Always use forward slashes (/) in database, even on Windows
# This ensures database portability across platforms

def to_relative_path(absolute_path: Path) -> str:
    """Convert absolute Dropbox path to relative path for database storage.

    Args:
        absolute_path: Absolute path within Dropbox

    Returns:
        Relative path string with forward slashes (e.g., 'projects/proj-001/images/img-xxx.jpg')

    Note:
        Always uses forward slashes (/) regardless of platform for database consistency.

    Example:
        macOS:   /Users/songym/Dropbox/.../img.jpg   -> 'projects/.../img.jpg'
        Windows: C:\\Users\\songym\\Dropbox\\...\\img.jpg -> 'projects/.../img.jpg'
    """
    _check_dropbox_available()
    try:
        rel_path = absolute_path.relative_to(DROPBOX_ROOT)
        # Convert to POSIX-style path (forward slashes) for database
        return rel_path.as_posix()
    except ValueError:
        raise ValueError(
            f"Path {absolute_path} is not within Dropbox root {DROPBOX_ROOT}"
        )


def from_relative_path(relative_path: str) -> Path:
    """Convert relative path (from database) to absolute Dropbox path.

    Args:
        relative_path: Relative path string from database (with forward slashes)

    Returns:
        Absolute path on this machine (platform-specific)

    Note:
        Input should always use forward slashes (/) as stored in database.
        Output Path object handles platform-specific separators automatically.

    Example:
        Database: 'projects/test/images/img-001.jpg'
        macOS:    /Users/songym/Dropbox/.../img-001.jpg
        Windows:  C:\\Users\\songym\\Dropbox\\...\\img-001.jpg
    """
    _check_dropbox_available()
    # Path automatically handles forward slashes on all platforms
    return DROPBOX_ROOT / relative_path


# =================================================================
# Validation (Cross-Platform)
# =================================================================

def validate_dropbox_setup() -> dict:
    """Validate that Dropbox is properly set up on this machine.

    Returns:
        Dict with validation results:
        {
            'platform': str,
            'dropbox_installed': bool,
            'base_dir_exists': bool,
            'writable': bool,
            'dropbox_root': str,
            'errors': list[str],
            'warnings': list[str]
        }
    """
    results = {
        'platform': PLATFORM,
        'dropbox_installed': False,
        'base_dir_exists': False,
        'writable': False,
        'dropbox_root': str(DROPBOX_ROOT) if DROPBOX_ROOT else None,
        'errors': [],
        'warnings': []
    }

    if not DROPBOX_AVAILABLE:
        results['errors'].append(DROPBOX_ERROR)
        return results

    # Check if Dropbox base exists
    if not DROPBOX_BASE.exists():
        results['errors'].append(
            f"Dropbox base directory not found: {DROPBOX_BASE}"
        )
        return results

    results['dropbox_installed'] = True

    # Check if our base directory exists
    if not DROPBOX_ROOT.exists():
        results['errors'].append(
            f"Project directory {DROPBOX_ROOT} does not exist and could not be created."
        )
        return results

    results['base_dir_exists'] = True

    # Check if we can write to the directory
    try:
        test_file = DROPBOX_ROOT / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        results['writable'] = True
    except Exception as e:
        results['errors'].append(
            f"Cannot write to {DROPBOX_ROOT}: {str(e)}"
        )

    # Platform-specific warnings
    if PLATFORM == 'Windows':
        # Check for long path support on Windows
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\FileSystem"
            )
            value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
            if value != 1:
                results['warnings'].append(
                    "Windows Long Paths not enabled. May cause issues with deep directory structures. "
                    "Enable via: Registry Editor -> HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem "
                    "-> LongPathsEnabled = 1"
                )
        except:
            pass  # Can't check, skip warning

    return results


# =================================================================
# Cleanup Utilities
# =================================================================

def cleanup_temp_downloads() -> int:
    """Clean up temporary download files.

    Returns:
        Number of files deleted
    """
    if not DROPBOX_AVAILABLE:
        return 0

    downloads_dir = TEMP_ROOT / "downloads"
    if not downloads_dir.exists():
        return 0

    count = 0
    for file_path in downloads_dir.iterdir():
        if file_path.is_file():
            try:
                file_path.unlink()
                count += 1
            except Exception:
                pass  # Skip files that can't be deleted

    return count


def get_project_size(project_id: str) -> int:
    """Get total size of all files in a project (in bytes).

    Args:
        project_id: Project UUID or slug

    Returns:
        Total size in bytes
    """
    if not DROPBOX_AVAILABLE:
        return 0

    project_path = get_project_path(project_id)
    total_size = 0

    for file_path in project_path.rglob('*'):
        if file_path.is_file():
            try:
                total_size += file_path.stat().st_size
            except Exception:
                pass  # Skip files that can't be accessed

    return total_size


def format_size(size_bytes: int) -> str:
    """Format size in bytes to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., '1.5 GB', '234 MB')
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


# =================================================================
# Module-level Validation (runs on import)
# =================================================================

def _check_setup_on_import():
    """Print warning if Dropbox setup has issues."""
    validation = validate_dropbox_setup()
    if validation['errors']:
        import warnings
        warnings.warn(
            f"Dropbox setup issues on {PLATFORM}:\n" +
            "\n".join(f"  - {err}" for err in validation['errors']),
            UserWarning
        )
    elif validation['warnings']:
        import warnings
        warnings.warn(
            f"Dropbox setup warnings on {PLATFORM}:\n" +
            "\n".join(f"  - {warn}" for warn in validation['warnings']),
            UserWarning
        )

# Run validation when module is imported
_check_setup_on_import()


# =================================================================
# Example Usage & Testing
# =================================================================

if __name__ == "__main__":
    print("Dropbox Path Configuration - Cross-Platform Demo")
    print("=" * 70)

    # Platform info
    print(f"\n1. Platform Information:")
    print(f"   OS: {PLATFORM}")
    print(f"   Python: {sys.version.split()[0]}")

    # Validation
    print(f"\n2. Dropbox Validation:")
    validation = validate_dropbox_setup()
    for key, value in validation.items():
        if key not in ['errors', 'warnings']:
            print(f"   {key}: {value}")

    if validation['errors']:
        print(f"\n   Errors:")
        for err in validation['errors']:
            print(f"     - {err}")

    if validation['warnings']:
        print(f"\n   Warnings:")
        for warn in validation['warnings']:
            print(f"     - {warn}")

    if not DROPBOX_AVAILABLE:
        print("\n⚠️  Dropbox not available. Cannot demonstrate path generation.")
        sys.exit(1)

    # Base paths
    print(f"\n3. Base Paths:")
    print(f"   Dropbox base: {DROPBOX_BASE}")
    print(f"   Project root: {DROPBOX_ROOT}")
    print(f"   Projects: {PROJECTS_ROOT}")
    print(f"   Temp: {TEMP_ROOT}")

    # Generate sample paths
    project_id = "20250107-landscape"
    pass_id = "pass-001"
    node_id = "a1b2c3d4-5678-90ab-cdef-1234567890ab"

    print(f"\n4. Generated Paths (project: '{project_id}'):")
    print(f"   Project: {get_project_path(project_id)}")
    print(f"   Pass: {get_pass_path(project_id, pass_id)}")
    print(f"   Images: {get_images_path(project_id, pass_id)}")
    print(f"   Videos: {get_videos_path(project_id, pass_id)}")
    print(f"   Exports: {get_exports_path(project_id)}")

    # Node file paths
    print(f"\n5. Node File Paths:")
    video_path = get_node_file_path(project_id, pass_id, node_id, "video", "mp4")
    image_path = get_node_file_path(project_id, pass_id, node_id, "image", "jpg")
    print(f"   Video: {video_path}")
    print(f"   Image: {image_path}")

    # Relative paths (for database)
    print(f"\n6. Database Paths (always forward slashes):")
    video_rel = to_relative_path(video_path)
    image_rel = to_relative_path(image_path)
    print(f"   Video: {video_rel}")
    print(f"   Image: {image_rel}")

    # Convert back
    print(f"\n7. Convert Back to Absolute:")
    video_abs = from_relative_path(video_rel)
    print(f"   Database: {video_rel}")
    print(f"   Absolute: {video_abs}")
    print(f"   Match: {video_abs == video_path}")

    # Platform-specific notes
    print(f"\n8. Platform-Specific Notes:")
    if PLATFORM == 'Windows':
        print(f"   - Using backslashes in absolute paths: {str(video_path)}")
        print(f"   - Database uses forward slashes: {video_rel}")
        print(f"   - Path separators handled automatically by pathlib")
    else:
        print(f"   - Using forward slashes natively")
        print(f"   - No conversion needed between OS and database format")

    print(f"\n✅ Cross-platform path configuration validated successfully!")
