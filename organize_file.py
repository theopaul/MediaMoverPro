import os
import shutil
import logging
from datetime import datetime

# === Configuration ===

# Logging configuration
error_log = "./ErrorLog.txt"
logging.basicConfig(filename=error_log, level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

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

def get_file_date(file_path):
    """
    Returns the earliest date between creation and modification of the file.
    """
    try:
        file_creation_date = datetime.fromtimestamp(os.path.getctime(file_path))
        file_modification_date = datetime.fromtimestamp(os.path.getmtime(file_path))
        return min(file_creation_date, file_modification_date)
    except Exception as e:
        logging.error(f"Error obtaining dates for file {file_path}: {e}")
        return None

def generate_new_name(file_date, file_ext, existing_names):
    """
    Generates a unique filename based on the date and time.
    Format: YYYYMMDD_HHMMSS.ext
    If duplicate exists, appends an incremental suffix: _0001, _0002, etc.
    """
    base_name = file_date.strftime('%Y%m%d_%H%M%S')
    new_name = f"{base_name}.{file_ext.lower()}"
    counter = 1

    # Increment suffix until a unique name is found
    while new_name in existing_names:
        suffix = f"_{counter:04d}"
        new_name = f"{base_name}{suffix}.{file_ext.lower()}"
        counter += 1

    existing_names.add(new_name)
    return new_name

def categorize_file(file_ext):
    """
    Determines the category of a non-identified file based on its extension.
    Returns the category name or 'Others' if not found.
    """
    for category, extensions in non_identify_categories.items():
        if file_ext.upper() in extensions:
            return category
    return "Others"

def remove_empty_folders(directory):
    """
    Recursively removes empty folders.
    """
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_ in dirs:
            dir_path = os.path.join(root, dir_)
            try:
                os.rmdir(dir_path)  # Removes directory if empty
                print(f"Removed empty directory: {dir_path}")
            except OSError:
                pass  # Directory not empty or cannot be removed

def move_files(src_directory, dest_directory):
    """
    Moves and organizes files from the source directory to the destination directory.
    """
    if not os.path.exists(src_directory):
        error_message = f"Error: Source directory '{src_directory}' does not exist."
        print(error_message)
        logging.error(error_message)
        return

    if not os.path.exists(dest_directory):
        try:
            os.makedirs(dest_directory, exist_ok=True)
            print(f"Created destination directory: {dest_directory}")
        except Exception as e:
            error_message = f"Error creating destination directory '{dest_directory}': {e}"
            print(error_message)
            logging.error(error_message)
            return

    # Set to keep track of existing names to handle duplicates
    existing_names = set()

    for root, dirs, files in os.walk(src_directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.exists(file_path):  # Check if file still exists
                continue

            try:
                # Check file size
                file_size = os.path.getsize(file_path)
                file_ext = file.split('.')[-1].upper()

                # Handle small files but keep specific extensions in correct folders
                if file_size < 1024 and file_ext not in ['IPYNB', 'PY', 'SQL', 'TXT']:
                    # Handle small items
                    file_date = get_file_date(file_path)
                    if not file_date:
                        continue  # Skip files with undetermined dates

                    year = file_date.strftime("%Y")
                    target_dir = os.path.join(dest_directory, "Non Identify Items", "Small Items", year)
                    os.makedirs(target_dir, exist_ok=True)

                    new_name = file  # No renaming for small items

                    # Ensure unique filename within the target directory
                    if os.path.exists(os.path.join(target_dir, new_name)):
                        name, ext = os.path.splitext(file)
                        counter = 1
                        while True:
                            new_name = f"{name}_{counter:04d}{ext}"
                            if not os.path.exists(os.path.join(target_dir, new_name)):
                                break
                            counter += 1

                    new_full_path = os.path.join(target_dir, new_name)

                else:
                    # Handle based on file extension
                    if file_ext in photo_video_extensions:
                        # Handle photos and videos
                        folder_type = photo_video_extensions[file_ext]
                        file_date = get_file_date(file_path)
                        if not file_date:
                            continue  # Skip files with undetermined dates

                        year = file_date.strftime("%Y")
                        month_year = file_date.strftime("%m.%Y")

                        # Determine if the file is a photo or video
                        if folder_type in ['RAW Files', 'HEIC', 'AAE', 'JPG', 'PNG', 'GIF', 'TIF', 'DNG', 'GPR']:
                            category_folder = "Photos"
                        elif folder_type in photo_video_extensions.values():  # Video formats
                            category_folder = "Videos"
                        else:
                            category_folder = "Others"

                        target_dir = os.path.join(dest_directory, year, month_year, category_folder, folder_type)
                        os.makedirs(target_dir, exist_ok=True)

                        new_name = generate_new_name(file_date, file_ext, existing_names)
                    else:
                        # Handle Non Identify Items or specific extensions regardless of size
                        if file_ext in ['IPYNB', 'PY', 'SQL', 'TXT']:
                            category = categorize_file(file_ext)
                        else:
                            category = categorize_file(file_ext)
                        
                        file_date = get_file_date(file_path)
                        if not file_date:
                            continue  # Skip files with undetermined dates

                        year = file_date.strftime("%Y")
                        month_year = file_date.strftime("%m.%Y")
                        target_dir = os.path.join(dest_directory, "Non Identify Items", category, year, month_year)
                        os.makedirs(target_dir, exist_ok=True)
                        new_name = file  # No renaming for non-identified items

                        # Ensure unique filename within the target directory
                        if os.path.exists(os.path.join(target_dir, new_name)):
                            name, ext = os.path.splitext(file)
                            counter = 1
                            while True:
                                new_name = f"{name}_{counter:04d}{ext}"
                                if not os.path.exists(os.path.join(target_dir, new_name)):
                                    break
                                counter += 1

                    new_full_path = os.path.join(target_dir, new_name)

                # Move the file
                shutil.move(file_path, new_full_path)
                print(f"Moved: {file_path} -> {new_full_path}")

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
    remove_empty_folders(src_directory)

# === Main Execution ===

if __name__ == "__main__":
    try:
        # Prompt user for source and destination directories
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
