import os
from video_utils import get_mp4_files_by_folder
from gui import GridScroller
from constants import DESTINATION_PATH

if __name__ == "__main__":
    if os.path.isdir(DESTINATION_PATH):
        folder_file_data = get_mp4_files_by_folder(DESTINATION_PATH)
        app = GridScroller(folder_file_data, DESTINATION_PATH)
        app.mainloop()
    else:
        print("Invalid directory.")
