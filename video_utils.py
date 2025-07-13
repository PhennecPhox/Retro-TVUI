import os
import subprocess
import json
import re

def get_mp4_files_by_folder(destination):
    folder_files = []
    for root, dirs, files in os.walk(destination):
        mp4_files = [f for f in files if f.lower().endswith('.mp4') and f.lower() != 'advert.mp4']
        if mp4_files:
            rel_folder = os.path.relpath(root, destination)
            folder_files.append((rel_folder, mp4_files))
    return folder_files

def get_video_description(filepath):
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_entries", "format_tags=comment:format_tags=description",
            filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        tags = data.get("format", {}).get("tags", {})
        desc = tags.get("description") or tags.get("comment") or "No description available."
        return desc.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore").strip()
    except Exception:
        return "No description available."

def clean_filename(filename):
    name = os.path.splitext(filename)[0]
    name = re.sub(r"^\d+\s*", "", name)
    name = re.sub(r"\s*\(.*?\)", "", name)
    return name.strip()
