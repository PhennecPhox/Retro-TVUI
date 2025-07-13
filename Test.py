import os
import tkinter as tk
from tkinter import ttk
import vlc
import subprocess
from datetime import datetime, timedelta
import json

# Example directory for video previews
VIDEO_DIR = r"C:\Users\Wyatt\Videos\Captures"
CHANNELS = sorted([
    d for d in os.listdir(VIDEO_DIR)
    if os.path.isdir(os.path.join(VIDEO_DIR, d))
])
  # Folders = channels

# Create time slots
TIME_SLOTS = [datetime(2025, 1, 1, 18, 0) + timedelta(minutes=30 * i) for i in range(24)]  # 6PM to 6AM

# Helper: Get video metadata
def get_metadata(file_path):
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', '-show_streams', file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    metadata = json.loads(result.stdout)
    try:
        duration = float(metadata["format"]["duration"])
        desc = metadata["format"].get("tags", {}).get("comment", "No description.")
    except:
        duration = 0
        desc = "No description."
    return duration, desc

class TVGuideApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TV Guide")
        self.selected_row = 0
        self.selected_col = 0

        # Main container
        self.container = tk.Frame(root)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Top preview frame
        self.top_frame = tk.Frame(self.container)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.video_panel = tk.Frame(self.top_frame, width=320, height=240, bg="black")
        self.video_panel.pack(side=tk.RIGHT, padx=10, pady=5)
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.set_hwnd(self.video_panel.winfo_id())  # Windows
        # For Linux: self.player.set_xwindow(self.video_panel.winfo_id())

        # Scrollable canvas
        self.canvas = tk.Canvas(self.container, bg="black", height=400)
        self.x_scroll = ttk.Scrollbar(self.container, orient="horizontal", command=self.canvas.xview)
        self.y_scroll = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.x_scroll.set, yscrollcommand=self.y_scroll.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.grid_frame = tk.Frame(self.canvas, bg="black")
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")

        self.program_buttons = []  # For navigation

        self.build_time_bar()
        self.build_channel_grid()

        self.grid_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)

        self.highlight_selection()
        self.play_preview()

    def build_time_bar(self):
        header = tk.Frame(self.grid_frame, bg="gray20")
        header.grid(row=0, column=1, columnspan=len(TIME_SLOTS))
        for j, slot in enumerate(TIME_SLOTS):
            label = tk.Label(header, text=slot.strftime('%I:%M %p'), bg="gray20", fg="white",
                             width=15, borderwidth=1, relief="ridge")
            label.grid(row=0, column=j)

    def build_channel_grid(self):
        for i, channel in enumerate(CHANNELS):
            row_frame = tk.Frame(self.grid_frame, bg="gray10")
            row_frame.grid(row=i+1, column=0, columnspan=len(TIME_SLOTS)+1)

            label = tk.Label(row_frame, text=channel, bg="gray30", fg="white",
                             width=15, anchor='w', borderwidth=1, relief="ridge")
            label.grid(row=0, column=0)

            row_buttons = []
            files = sorted(os.listdir(os.path.join(VIDEO_DIR, channel)))
            for j in range(len(TIME_SLOTS)):
                if j < len(files):
                    file = files[j]
                    filepath = os.path.join(VIDEO_DIR, channel, file)
                    name = os.path.splitext(file)[0]
                    duration, desc = get_metadata(filepath)
                    text = f"{name}\n{int(duration)//60} min"
                    btn = tk.Button(row_frame, text=text, bg="gray25", fg="white", wraplength=100,
                                    width=15, height=2, borderwidth=1, relief="groove")
                    btn.filepath = filepath
                    btn.desc = desc
                    btn.grid(row=0, column=j+1)
                    row_buttons.append(btn)
            self.program_buttons.append(row_buttons)

    def play_video(self, path):
        media = self.instance.media_new(path)
        self.player.set_media(media)
        self.player.play()

    def highlight_selection(self):
        for i, row in enumerate(self.program_buttons):
            for j, btn in enumerate(row):
                if i == self.selected_row and j == self.selected_col:
                   btn.config(bg="dodgerblue")
                else:
                  btn.config(bg="gray25")

       # Play ADVERT.mp4 from selected channel
        channel_name = CHANNELS[self.selected_row]
        advert_path = os.path.join(VIDEO_DIR, channel_name, "ADVERT.mp4")
        if os.path.exists(advert_path):
           self.play_video(advert_path)


    def play_preview(self):
        if self.program_buttons:
            try:
                btn = self.program_buttons[self.selected_row][self.selected_col]
                self.play_video(btn.filepath)
            except IndexError:
                pass

    def move_up(self, event):
        self.selected_row = max(0, self.selected_row - 1)
        self.highlight_selection()

    def move_down(self, event):
        self.selected_row = min(len(self.program_buttons) - 1, self.selected_row + 1)
        self.highlight_selection()

    def move_left(self, event):
        self.selected_col = max(0, self.selected_col - 1)
        self.highlight_selection()

    def move_right(self, event):
        self.selected_col = min(len(self.program_buttons[0]) - 1, self.selected_col + 1)
        self.highlight_selection()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1280x720")
    app = TVGuideApp(root)
    root.mainloop()
