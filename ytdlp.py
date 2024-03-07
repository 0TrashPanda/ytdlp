import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog
from multiprocessing import Pool

def download_item(args):
    index, playlist_url, save_path = args
    try:
        subprocess.run([
            'yt-dlp',
            '--embed-thumbnail',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '5',
            '--add-metadata',
            '--playlist-items', str(index),
            '--output', f'{save_path}/%(title)s.%(ext)s',
            playlist_url
        ], check=True)
        print(f"Item {index} downloaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading item {index}: {e}")

def download_playlist(playlist_url, start_index, end_index, save_path):
    # Create a pool of processes
    with Pool() as pool:
        # Create a list of arguments for each item in the range
        args_list = [(index, playlist_url, save_path) for index in range(start_index, end_index + 1)]
        # Map the download_item function to the pool of processes
        pool.map(download_item, args_list)

def get_inputs():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Prompt the user for the playlist URL, start index, and end index
    playlist_url = simpledialog.askstring(title="Playlist Downloader", prompt="Enter the playlist URL:")
    start_index = simpledialog.askinteger(title="Playlist Downloader", prompt="Enter the start index:")
    end_index = simpledialog.askinteger(title="Playlist Downloader", prompt="Enter the end index:")

    # Ask user to select download path
    save_path = filedialog.askdirectory(title="Select Save Path")

    return playlist_url, start_index, end_index, save_path

def main():
    playlist_url, start_index, end_index, save_path = get_inputs()
    if playlist_url and start_index is not None and end_index is not None and save_path:
        download_playlist(playlist_url, start_index, end_index, save_path)
    else:
        print("Invalid input.")

if __name__ == "__main__":
    main()
