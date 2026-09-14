import os
# Type in the path e.g C:/Users/username/...
folder_path = input('Type in the folder path (including the name of the folder to create):\n')
os.mkdir(folder_path)

path_name_original = input('Paste the original path:\n')
path_name_destination = folder_path
folder_original = path_name_original
folder_destination = path_name_destination



entries = os.scandir(folder_original)

for entry in entries:
    location_original = os.path.join(folder_original, entry.name)
    location_destination = os.path.join(folder_destination, entry.name)
    if os.path.isfile(location_original):
        os.rename(location_original,location_destination)