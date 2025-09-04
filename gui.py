import os
import tkinter as tk
import vlc
from datetime import datetime, timedelta
import math
from tkinter import PhotoImage
from video_utils import get_video_description, clean_filename, get_video_duration
from constants import LEFT_LOGO_PATH, RIGHT_LOGO_PATH

class GridScroller(tk.Tk):
    def __init__(self, folder_file_data, destination_path):
        super().__init__()
        self.title("MP4 Grid with ADVERT Video")
        self.geometry("640x480")

        self.description_label = tk.Label(self, text="", font=("Arial", 12), wraplength=310, justify="left", anchor="nw", bg="light blue")
        self.header_frame = tk.Frame(self, bg="navy", height=50)

        self.left_image = PhotoImage(file=LEFT_LOGO_PATH)
        self.right_image = PhotoImage(file=RIGHT_LOGO_PATH)

        tk.Label(self.header_frame, image=self.left_image, bg="navy").pack(side="left", padx=5)
        tk.Label(self.header_frame, text="TV Listings", bg="navy", fg="white", font=("Arial", 16, "bold")).pack(side="left", expand=True)
        tk.Label(self.header_frame, image=self.right_image, bg="navy").pack(side="right", padx=5)

        self.folder_file_data = folder_file_data
        self.destination_path = destination_path
        self.max_rows = len(folder_file_data)
        self.max_cols = max(len(files) for _, files in folder_file_data)
        self.visible_rows = 5
        self.visible_cols = 3
        self.visible_row_start = 0
        self.visible_col_start = 0
        self.highlight_row = 0
        self.highlight_col = 0
        self.button_map = {}

        self.video_frame = tk.Frame(self, bg="black")
        self.label_frame = tk.Frame(self, bg="navy")
        self.main_frame = tk.Frame(self)
        self.canvas = tk.Canvas(self.main_frame, bg="purple")
        self.canvas.pack(fill="both", expand=True)

        self.grid_frame = tk.Frame(self)
        self.grid_frame.place(x=0, y=0)

        self.grid_frame.lift(self.video_frame)
        self.grid_frame.lift(self.label_frame)
        self.grid_frame.lift(self.main_frame)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.after(100, self.update_frame_sizes)
        self.after(100, lambda: self.player.set_hwnd(self.video_frame.winfo_id()))

        self.create_all_buttons()
        self.layout_visible_grid()
        self.update_advert_video(self.highlight_row)
        self.update_description()

        self.bind("<Left>", self.move_left)
        self.bind("<Right>", self.move_right)
        self.bind("<Up>", self.move_up)
        self.bind("<Down>", self.move_down)
        self.focus_set()

    def update_description(self):
        try:
            folder, files = self.folder_file_data[self.highlight_row]
            if self.highlight_col < len(files):
                file_path = os.path.join(self.destination_path, folder, files[self.highlight_col])
                desc = get_video_description(file_path)
                self.description_label.config(text=desc)
            else:
                self.description_label.config(text="")
        except Exception:
            self.description_label.config(text="")

    def update_frame_sizes(self):
        win_width = self.winfo_width()
        win_height = self.winfo_height()

        video_width = win_width // 2
        video_height = win_height // 2
        header_height = 50
        desc_height = video_height - header_height
        content_width = win_width - video_width

        self.video_frame.place(relx=1.0, rely=0.0, anchor="ne", width=video_width, height=video_height)
        self.header_frame.place(x=0, y=0, width=content_width, height=header_height)
        self.description_label.place(x=0, y=header_height, width=content_width, height=desc_height)

        label_y = header_height + desc_height
        label_height = 30  # height of the timeline bar
        self.label_frame.place(x=0, y=label_y, width=win_width, height=label_height)
        self.main_frame.place(x=0, y=label_y + label_height, width=win_width, height=win_height - (label_y + label_height))

        try:
            self.player.set_hwnd(self.video_frame.winfo_id())
        except Exception:
            pass

        self.after(500, self.update_frame_sizes)

    def create_all_buttons(self):
        for row_index, (folder, files) in enumerate(self.folder_file_data):
            parts = folder.replace("\\", "/").split("/")
            display_name = f"{parts[-1]}\n{parts[-2]}" if len(parts) >= 2 else parts[-1]
            label = tk.Label(self.canvas, text=display_name, width=14, height=2, bg="steel blue", relief="raised", justify="center")
            self.button_map[(row_index, -1)] = label

            for col_index, filename in enumerate(files):
                file_path = os.path.join(self.destination_path, folder, filename)
                duration = get_video_duration(file_path)
                span = max(1, min(3, math.ceil(duration / 1800)))
                clean_name = clean_filename(filename)
                btn = tk.Button(self.canvas, text=clean_name)
                self.button_map[(row_index, col_index)] = (btn, span)

    def layout_visible_grid(self):
        self.canvas.delete("all")

        # Generate timeline labels
        for widget in self.label_frame.winfo_children():
            widget.destroy()

        now = datetime.now()
        start_time = now.replace(minute=0, second=0, microsecond=0)
        if now.minute >= 30:
            start_time += timedelta(minutes=30)
        start_time += timedelta(minutes=30 * self.visible_col_start)

        # Day label
        day_label = "Tomorrow" if start_time.day != now.day else "Today"
        tk.Label(self.label_frame, text=day_label, width=10, bg="navy", fg="white", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=2, pady=2)

        # Time slots
        for vc in range(self.visible_cols):
            slot_time = start_time + timedelta(minutes=30 * vc)
            time_str = slot_time.strftime("%I:%M%p").lstrip("0").lower().replace(":00", "")
            tk.Label(self.label_frame, text=time_str, width=23, bg="#ccc").grid(row=0, column=vc + 1, padx=1, pady=2)

        base_width = 170
        base_height = 42
        label_width = 110

        for (r, c), val in self.button_map.items():
            if self.visible_row_start <= r < self.visible_row_start + self.visible_rows:
                y = (r - self.visible_row_start) * base_height
                if c == -1:
                    self.canvas.create_window(0, y, window=val, width=label_width, height=base_height, anchor="nw")
                else:
                    btn, span = val
                    if self.visible_col_start <= c < self.visible_col_start + self.visible_cols:
                        x = (c - self.visible_col_start) * base_width + label_width
                        self.canvas.create_window(x, y, window=btn, width=base_width * span, height=base_height, anchor="nw")

        self.update_highlight()
        self.update_description()

    def update_highlight(self):
        for (r, c), value in self.button_map.items():
            if c != -1:
                btn, _ = value
                if r == self.highlight_row and c == self.highlight_col:
                    btn.configure(bg="orange")
                else:
                    btn.configure(bg="SystemButtonFace")

    def scroll_to_include(self, row, col):
        if row < self.visible_row_start:
            self.visible_row_start = row
        elif row >= self.visible_row_start + self.visible_rows:
            self.visible_row_start = row - self.visible_rows + 1
        if col < self.visible_col_start:
            self.visible_col_start = col
        elif col >= self.visible_col_start + self.visible_cols:
            self.visible_col_start = col - self.visible_cols + 1

    def move_left(self, event=None):
        if self.highlight_col > 0:
            self.highlight_col -= 1
        else:
            num_files = len(self.folder_file_data[self.highlight_row][1])
            self.highlight_col = num_files - 1 if num_files > 0 else 0
        self.scroll_to_include(self.highlight_row, self.highlight_col)
        self.layout_visible_grid()

    def move_right(self, event=None):
        num_files = len(self.folder_file_data[self.highlight_row][1])
        if self.highlight_col + 1 < num_files:
            self.highlight_col += 1
        else:
            self.highlight_col = 0
        self.scroll_to_include(self.highlight_row, self.highlight_col)
        self.layout_visible_grid()

    def move_up(self, event=None):
        prev_row = self.highlight_row - 1
        while prev_row >= 0:
            if self.highlight_col < len(self.folder_file_data[prev_row][1]):
                self.highlight_row = prev_row
                break
            prev_row -= 1
        else:
            prev_row = self.max_rows - 1
            while prev_row > self.highlight_row:
                if self.highlight_col < len(self.folder_file_data[prev_row][1]):
                    self.highlight_row = prev_row
                    break
                prev_row -= 1
        self.scroll_to_include(self.highlight_row, self.highlight_col)
        self.update_advert_video(self.highlight_row)
        self.layout_visible_grid()

    def move_down(self, event=None):
        next_row = self.highlight_row + 1
        while next_row < self.max_rows:
            if self.highlight_col < len(self.folder_file_data[next_row][1]):
                self.highlight_row = next_row
                break
            next_row += 1
        else:
            next_row = 0
            while next_row < self.highlight_row:
                if self.highlight_col < len(self.folder_file_data[next_row][1]):
                    self.highlight_row = next_row
                    break
                next_row += 1
        self.scroll_to_include(self.highlight_row, self.highlight_col)
        self.update_advert_video(self.highlight_row)
        self.layout_visible_grid()

    def update_advert_video(self, row_index):
        folder_path = os.path.join(self.destination_path, self.folder_file_data[row_index][0])
        advert_path = os.path.join(folder_path, "ADVERT.mp4")
        if os.path.isfile(advert_path):
            media = self.instance.media_new(advert_path)
            self.player.set_media(media)
            self.player.play()
            self.player.set_fullscreen(False)
