import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import subprocess

ydl_opts = {
    'quiet': True,
}
new_format = ''

def get_playlist_length():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a playlist URL")
        return

    length_label.config(text="Fetching...")
    length_button.config(state=tk.DISABLED)

    def fetch_length():
        ydl_opts = {"quiet": True, "extract_flat": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    length = len(info['entries'])
                    length_label.config(text=f"Playlist Length: {length}")
                    end_index_var.set(length - 1)  # Set default end index to last item
                else:
                    messagebox.showerror("Error", "Failed to fetch playlist info")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch playlist: {str(e)}")
        finally:
            length_button.config(state=tk.NORMAL)

    threading.Thread(target=fetch_length, daemon=True).start()

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        save_folder_var.set(folder)


def download_video(playlist_url, index):
    final_args = ydl_opts.copy()
    final_args['playlist_items'] = str(index + 1)
    print(f"Downloading video {index} from {playlist_url}")
    print(final_args)
    with yt_dlp.YoutubeDL(final_args) as ydl:
        ydl.download([playlist_url])

def download_video_cmd(playlist_url, index, output_path, format, embed_thumbnail):
    args = [
        'yt-dlp',
        '--extract-audio',
        '--audio-quality', '5',
        '--add-metadata',
        '--playlist-items', str(index),
        '--output', f'{output_path}/%(title)s.%(ext)s',
        playlist_url
    ]
    if embed_thumbnail:
        args += ['--embed-thumbnail']
    if format:
        args += ['--audio-format', format]
    subprocess.Popen(args)

def set_format(format):
    print(f'Setting format to {format}')
    global new_format
    match format:
        case 'm4a':
            format = 'm4a'
        case 'mp3':
            format = 'mp3'
        case 'default':
            return None
    global ydl_opts
    ydl_opts['format'] = f'bestaudio/best'
    ydl_opts['postprocessors'] += [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': format},
    ]
    return format

def download_playlist(start_index, end_index, url):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for i in range(start_index, end_index):
                threading.Thread(target=download_video, args=(url, i)).start()

def start_download():
    url = url_entry.get().strip()
    save_folder = save_folder_var.get().strip()
    start_index = start_index_var.get()
    end_index = end_index_var.get() + 1  # Ensure end index is inclusive
    format = format_var.get()
    embed_thumbnail = embed_thumbnail_var.get()
    dl_method = method_var.get()

    if not url or not save_folder:
        messagebox.showerror("Error", "Please fill in all fields")
        return
    if start_index < 0 or end_index <= start_index:
        messagebox.showerror("Error", "Invalid index range")
        return

    global ydl_opts
    ydl_opts["postprocessors"] = []
    ydl_opts['paths'] = {'home': save_folder}
    if embed_thumbnail:
        ydl_opts['postprocessors'] += [
        {'key': 'EmbedThumbnail'},
        {'key': 'FFmpegMetadata'},
    ]
    format = set_format(format)

    if dl_method == 'yt-dlpy':
        download_playlist(start_index, end_index, url)
    elif dl_method == 'old':
        for i in range(start_index, end_index + 1):
            download_video_cmd(url, i, save_folder, format, embed_thumbnail)

root = tk.Tk()
root.title("YouTube Playlist Downloader")
# root.geometry("500x250")
root.configure(padx=10, pady=10)

# Playlist URL
url_label = tk.Label(root, text="Playlist URL:")
url_label.grid(row=0, column=0, sticky="w", pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, columnspan=2, pady=5)

# Get Playlist Length Button
length_button = tk.Button(root, text="Get Length", command=get_playlist_length)
length_button.grid(row=0, column=3, padx=5, pady=5)

# Playlist Length Display
length_label = tk.Label(root, text="Playlist Length: N/A")
length_label.grid(row=1, column=1, columnspan=2, pady=5)

# Start Index
start_index_var = tk.IntVar(value=0)
start_label = tk.Label(root, text="Start Index:")
start_label.grid(row=2, column=0, sticky="w", pady=5)
start_entry = tk.Entry(root, textvariable=start_index_var, width=5)
start_entry.grid(row=2, column=1, pady=5)

# End Index
end_index_var = tk.IntVar(value=0)
end_label = tk.Label(root, text="End Index:")
end_label.grid(row=3, column=0, sticky="w", pady=5)
end_entry = tk.Entry(root, textvariable=end_index_var, width=5)
end_entry.grid(row=3, column=1, pady=5)

# Save Folder
save_folder_var = tk.StringVar()
save_folder_label = tk.Label(root, text="Save Folder:")
save_folder_label.grid(row=4, column=0, sticky="w", pady=5)
save_folder_entry = tk.Entry(root, textvariable=save_folder_var, width=40)
save_folder_entry.grid(row=4, column=1, columnspan=2, pady=5)
browse_button = tk.Button(root, text="Browse", command=browse_folder)
browse_button.grid(row=4, column=3, padx=5, pady=5)

# Download Method Dropdown
method_label = tk.Label(root, text="Download Method:")
method_label.grid(row=5, column=0, sticky="w", pady=5)
method_var = tk.StringVar(value="yt-dlpy")
method_dropdown = ttk.Combobox(root, textvariable=method_var, values=["yt-dlpy", "old"], state="readonly")
method_dropdown.grid(row=5, column=1, columnspan=2, pady=5)

# Format Dropdown
format_label = tk.Label(root, text="Select Format:")
format_label.grid(row=6, column=0, sticky="w", pady=5)
format_var = tk.StringVar(value="default")
format_dropdown = ttk.Combobox(root, textvariable=format_var, values=["default", "mp3", "m4a"], state="readonly")
format_dropdown.grid(row=6, column=1, columnspan=2, pady=5)

# Embed Thumbnail Checkbox
embed_thumbnail_var = tk.BooleanVar(value=True)  # Default value is True (checked)
embed_thumbnail_checkbox = tk.Checkbutton(root, text="Embed Thumbnail", variable=embed_thumbnail_var)
embed_thumbnail_checkbox.grid(row=7, column=1, columnspan=2, pady=5)

# Download Button
download_button = tk.Button(root, text="Download", command=start_download, bg="green", fg="white")
download_button.grid(row=8, column=1, columnspan=2, pady=10)

root.mainloop()
