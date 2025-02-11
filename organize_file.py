import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

# === Configuration ===

# Logging configuration
error_log = "./ErrorLog.txt"
logging.basicConfig(
    filename=error_log,
    level=logging.INFO,  # Now logging at INFO level to capture normal activity
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# File extension categories for Non Identify Items
non_identify_categories = {
    'Adobe Photoshop Files': ['PSD'],
    'Adobe Audition Files': ['CFA', 'SESX'],
    'VBA Files': ['VBA'],
    'Compressed Files': ['ZIP', 'RAR', '7Z', 'TAR', 'GZ', 'PKG', 'DMG'],
    'CSV Files': ['CSV'],
    'Fonts': ['TTF', 'OTF', 'FON', 'WOFF', 'WOFF2'],
    'Adobe Illustrator Files': ['EPS', 'AI'],
    'Microsoft Files': ['DOCX', 'DOC', 'XLSX', 'XLS', 'PPTX', 'PPT'],
    'Music': ['MP3', 'WAV', 'FLAC', 'AAC', 'OGG', 'M4A'],
    'Notes': ['TXT'],
    'PDF Files': ['PDF'],
    'Python Files': ['PY', 'IPYNB'],
    'SRT Files': ['SRT'],
    'SQL Files': ['SQL']
    # Add more categories and extensions as needed
}

# Supported photo and video extensions
photo_video_extensions = {
    # Photos
    'NEF': 'RAW Files',
    'ARW': 'RAW Files',
    'CR3': 'RAW Files',
    'CR2': 'RAW Files',
    'RAF': 'RAW Files',
    'HEIC': 'HEIC',
    'AAE': 'AAE',
    'JPG': 'JPG',
    'JPEG': 'JPG',
    'PNG': 'PNG',
    'GIF': 'GIF',
    'TIF': 'TIF',
    'DNG': 'DNG',
    'GPR': 'GPR',
    
    # Videos
    'MOV': 'MOV',
    'MP4': 'MP4',
    'MPG': 'MPG',
    'AVI': 'AVI',
    'WMV': 'WMV',
    'ASF': 'ASF',
    'MPEG': 'MPEG',
    'FLV': 'FLV',
    'LRV': 'LRV',
    '3GP': '3GP',
    'M4V': 'M4V',
    'MKV': 'MKV',
    'MTS': 'MTS',
}

# === Helper Functions ===

def get_file_date(file_path: Path) -> datetime:
    """
    Returns the earliest date between creation and modification of the file.
    If an error occurs, returns None.
    """
    try:
        file_creation_date = datetime.fromtimestamp(file_path.stat().st_ctime)
        file_modification_date = datetime.fromtimestamp(file_path.stat().st_mtime)
        return min(file_creation_date, file_modification_date)
    except Exception as e:
        logging.error(f"Error obtaining dates for file {file_path}: {e}")
        return None

def categorize_file(file_ext: str) -> str:
    """
    Determines the category of a non-identified file based on its extension.
    Returns the category name or 'Others' if not found.
    """
    file_ext_upper = file_ext.upper()
    for category, extensions in non_identify_categories.items():
        if file_ext_upper in extensions:
            return category
    return "Others"

def remove_empty_folders(directory: Path) -> None:
    """
    Recursively removes empty folders in the given directory.
    """
    for root, dirs, _ in os.walk(directory, topdown=False):
        for d in dirs:
            dir_path = Path(root) / d
            try:
                dir_path.rmdir()  # Removes directory if empty
                print(f"Removed empty directory: {dir_path}")
                logging.info(f"Removed empty directory: {dir_path}")
            except OSError:
                pass  # Directory not empty or cannot be removed

def generate_unique_filename_in_dir(target_dir: Path, original_name: str) -> str:
    """
    Checks if a file with 'original_name' exists in 'target_dir'.
    If it does, appends an incremental suffix until a unique name is found.
    Returns the final unique filename (without the full path).
    """
    base_name, ext = os.path.splitext(original_name)
    candidate = original_name
    counter = 1
    
    while (target_dir / candidate).exists():
        candidate = f"{base_name}_{counter:04d}{ext}"
        counter += 1
    return candidate

def generate_new_name_from_date(file_date: datetime, file_ext: str, existing_names: set) -> str:
    """
    Generates a unique filename based on the date and time, in the format: YYYYMMDD_HHMMSS.ext
    If a duplicate is found within 'existing_names', appends an incremental suffix _0001, _0002, etc.
    """
    base_name = file_date.strftime('%Y%m%d_%H%M%S')
    new_name = f"{base_name}.{file_ext.lower()}"
    counter = 1
    
    while new_name in existing_names:
        new_name = f"{base_name}_{counter:04d}.{file_ext.lower()}"
        counter += 1
    
    existing_names.add(new_name)
    return new_name

def move_small_file(file_path: Path, dest_directory: Path, existing_names: set) -> None:
    """
    Handles moving of small files (<1KB) that are NOT in ['IPYNB', 'PY', 'SQL', 'TXT'].
    They are placed under 'Non Identify Items/Small Items/<Year>/'.
    """
    file_date = get_file_date(file_path)
    if not file_date:
        # Fallback to current date if we can't determine the file date
        file_date = datetime.now()
    
    year = file_date.strftime("%Y")
    target_dir = dest_directory / "Non Identify Items" / "Small Items" / year
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # We keep the original name, but ensure uniqueness
    new_name = generate_unique_filename_in_dir(target_dir, file_path.name)
    new_full_path = target_dir / new_name
    
    shutil.move(str(file_path), str(new_full_path))
    logging.info(f"Moved small file: {file_path} -> {new_full_path}")
    print(f"Moved small file: {file_path} -> {new_full_path}")

def move_photo_or_video(file_path: Path, file_ext: str, dest_directory: Path, existing_names: set) -> None:
    """
    Handles moving of photo/video files, placing them in:
      <Year>/<Month.Year>/<Photos or Videos>/<Extension Folder>.
    """
    folder_type = photo_video_extensions[file_ext.upper()]
    file_date = get_file_date(file_path)
    if not file_date:
        file_date = datetime.now()  # fallback if date can't be determined
    
    year = file_date.strftime("%Y")
    month_year = file_date.strftime("%m.%Y")

    # Determine if it's a photo or a video (by checking if folder_type is in a known set).
    # The dictionary is used for both photos and videos, so let's pick logically:
    photo_exts = {'RAW Files', 'HEIC', 'AAE', 'JPG', 'PNG', 'GIF', 'TIF', 'DNG', 'GPR'}
    if folder_type in photo_exts:
        category_folder = "Photos"
    else:
        category_folder = "Videos"

    target_dir = dest_directory / year / month_year / category_folder / folder_type
    target_dir.mkdir(parents=True, exist_ok=True)
    
    new_name = generate_new_name_from_date(file_date, file_ext, existing_names)
    new_full_path = target_dir / new_name

    shutil.move(str(file_path), str(new_full_path))
    logging.info(f"Moved photo/video: {file_path} -> {new_full_path}")
    print(f"Moved photo/video: {file_path} -> {new_full_path}")

def move_non_identified_file(file_path: Path, file_ext: str, dest_directory: Path) -> None:
    """
    Handles moving of non-photo/video files (or certain small text-based extensions).
    Places them under 'Non Identify Items/<Category>/<Year>/<Month.Year>/'.
    Keeps original filename but ensures uniqueness.
    """
    category = categorize_file(file_ext)
    file_date = get_file_date(file_path)
    if not file_date:
        file_date = datetime.now()

    year = file_date.strftime("%Y")
    month_year = file_date.strftime("%m.%Y")
    target_dir = dest_directory / "Non Identify Items" / category / year / month_year
    target_dir.mkdir(parents=True, exist_ok=True)
    
    new_name = generate_unique_filename_in_dir(target_dir, file_path.name)
    new_full_path = target_dir / new_name
    
    shutil.move(str(file_path), str(new_full_path))
    logging.info(f"Moved non-identified file: {file_path} -> {new_full_path}")
    print(f"Moved non-identified file: {file_path} -> {new_full_path}")

def move_files(src_directory: str, dest_directory: str) -> None:
    """
    Moves and organizes files from the source directory to the destination directory.
    """
    src_path = Path(src_directory)
    dest_path = Path(dest_directory)

    if not src_path.exists():
        error_message = f"Error: Source directory '{src_directory}' does not exist."
        print(error_message)
        logging.error(error_message)
        return

    if not dest_path.exists():
        try:
            dest_path.mkdir(parents=True, exist_ok=True)
            print(f"Created destination directory: {dest_directory}")
            logging.info(f"Created destination directory: {dest_directory}")
        except Exception as e:
            error_message = f"Error creating destination directory '{dest_directory}': {e}"
            print(error_message)
            logging.error(error_message)
            return

    # Set to keep track of date-based existing names (only for photo/video new_name collisions)
    existing_names = set()

    for root, dirs, files in os.walk(src_path):
        for f in files:
            file_path = Path(root) / f
            if not file_path.exists():
                continue  # File might have been moved or deleted

            try:
                file_size = file_path.stat().st_size
                file_ext = file_path.suffix[1:].upper()  # e.g., 'jpg' -> 'JPG'

                # Handle small files (<1KB) that are not in certain text-based extensions
                if file_size < 1024 and file_ext not in ['IPYNB', 'PY', 'SQL', 'TXT']:
                    move_small_file(file_path, dest_path, existing_names)
                else:
                    # Check if it's a photo or video
                    if file_ext in photo_video_extensions:
                        move_photo_or_video(file_path, file_ext, dest_path, existing_names)
                    else:
                        # Non-identified file or small standard text-based file
                        move_non_identified_file(file_path, file_ext, dest_path)

            except PermissionError as e:
                error_message = f"Permission error moving file {file_path}: {e}"
                print(error_message)
                logging.error(error_message)
                continue
            except Exception as e:
                error_message = f"Error processing file {file_path}: {e}"
                print(error_message)
                logging.error(error_message)
                continue

    # Remove empty folders after moving files
    remove_empty_folders(src_path)

# === Main Execution ===

if __name__ == "__main__":
    try:
        src_directory = input("Enter the path of the directory to organize: ").strip().strip('\'"')
        dest_directory = input("Enter the path of the destination directory: ").strip().strip('\'"')

        move_files(src_directory, dest_directory)
        print(f"Process completed. Check '{error_log}' for any error details.")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        print(error_message)
        logging.error(error_message)
