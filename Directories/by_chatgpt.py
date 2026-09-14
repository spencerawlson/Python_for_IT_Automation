import os
import shutil

# Ask the user for the original folder
folder = input('Enter the path of the folder you want to organize: ')

# Expand ~ to the user's home directory
folder = os.path.expanduser(folder)

# Ask the user for the name of the new folder
new_folder_name = input('Enter the name for the new folder: ')

# Create the main destination folder
cleaned_up = os.path.join(folder, new_folder_name)

os.makedirs(cleaned_up, exist_ok=True)

# Scan the original folder
entries = os.scandir(folder)

# Go through every item
for entry in entries:

    if entry.is_file():

        # Get the file extension
        extension = os.path.splitext(entry.name)[1].lower()

        # Determine the file type
        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            file_type = 'Images'

        elif extension in ['.mp4', '.mov', '.avi', '.mkv', '.wmv']:
            file_type = 'Videos'

        elif extension in ['.mp3', '.wav', '.flac', '.aac']:
            file_type = 'Audio'

        elif extension == '.pdf':
            file_type = 'PDF'

        elif extension in ['.doc', '.docx', '.odt']:
            file_type = 'Documents'

        elif extension in ['.txt', '.md']:
            file_type = 'Text'

        elif extension in ['.py', '.js', '.html', '.css', '.java', '.cpp']:
            file_type = 'Code'

        elif extension in ['.csv', '.xls', '.xlsx']:
            file_type = 'Spreadsheets'

        elif extension in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            file_type = 'Archives'

        else:
            file_type = 'Other'

        # Create the category folder
        destination_folder = os.path.join(
            cleaned_up,
            file_type
        )

        os.makedirs(destination_folder, exist_ok=True)

        # Create the complete destination path
        destination = os.path.join(
            destination_folder,
            entry.name
        )

        # Move the file
        shutil.move(entry.path, destination)

        print(f'Moved: {entry.name} → {file_type}')

print('\nFile organization complete!')