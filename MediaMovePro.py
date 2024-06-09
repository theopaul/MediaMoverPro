import os
import shutil
import random
import logging
from datetime import datetime

# Configure logging
error_log = "./ErrorLog.txt"
logging.basicConfig(filename=error_log, level=logging.ERROR)

# Prompt user for the directory to organize and remove surrounding quotes
src_directory = input("Enter the path to the directory you want to organize: ").strip().strip('\'"')
dest_directory = input("Enter the path to the destination directory: ").strip().strip('\'"')

# File extensions and corresponding folders
extension_folders = {
    'NEF': 'Photos/RAW Files',
    'ARW': 'Photos/RAW Files',
    'CR3': 'Photos/RAW Files',
    'CR2': 'Photos/RAW Files',
    'RAF': 'Photos/RAW Files',
    'HEIC': 'Photos/HEIC',
    'JPG': 'Photos/JPG',
    'JPEG': 'Photos/JPG',
    'PNG': 'Photos/PNG',
    'GIF': 'Photos/GIF',
    'TIF': 'Photos/TIF',
    'DNG': 'Photos/DNG',
    'GPR': 'Photos/GPR',
    'MOV': 'Videos',
    'MP4': 'Videos',
    'MPG': 'Videos',
    'AVI': 'Videos',
    'WMV': 'Videos',
    'WMA': 'Videos',
    'ASF': 'Videos',
    'MPEG': 'Videos',
    'FLV': 'Videos',
    'LRV': 'Videos',
    '3GP': 'Videos',
    'M4V': 'Videos',
    'MKV': 'Videos',
    'MTS': 'Videos',
    'WAV': 'Audio',
    'MP3': 'Audio',
}

def move_files(src_directory, dest_directory):
    if not os.path.exists(src_directory):
        error_message = f"Error: The directory '{src_directory}' does not exist. Please check the path and try again."
        print(error_message)
        logging.error(error_message)
        return

    if not os.path.exists(dest_directory):
        os.makedirs(dest_directory, exist_ok=True)
        print(f"Destination directory '{dest_directory}' created.")

    for root, dirs, files in os.walk(src_directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.exists(file_path):  # Check if the file still exists before processing
                continue

            try:
                file_ext = file.split('.')[-1].upper()
                file_creation_date = datetime.fromtimestamp(os.path.getctime(file_path))
                year = file_creation_date.strftime("%Y")
                month_year = file_creation_date.strftime("%m.%Y")
                folder = extension_folders.get(file_ext, "Others")

                if folder == "Others":
                    full_folder_path = os.path.join(dest_directory, folder, file_ext)
                else:
                    year_path = os.path.join(dest_directory, year)
                    month_year_path = os.path.join(year_path, month_year)
                    full_folder_path = os.path.join(month_year_path, folder)

                os.makedirs(full_folder_path, exist_ok=True)

                new_name = f"{file_creation_date.strftime('%Y-%m-%d')}_{file_ext}_{random.randint(10000, 999999)}.{file_ext.lower()}"
                new_full_path = os.path.join(full_folder_path, new_name)

                shutil.move(file_path, new_full_path)
                print(f"Moved: {file_path} to {new_full_path}")

            except PermissionError as e:
                error_message = f"Permission error moving file {file_path}. Error: {str(e)}"
                print(error_message)
                logging.error(error_message)
                continue
            except Exception as e:
                error_message = f"Error processing file {file_path}. Error: {str(e)}"
                print(error_message)
                logging.error(error_message)
                continue

if __name__ == "__main__":
    move_files(src_directory, dest_directory)

