import os
import sys
import threading
import time
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import datetime
import string

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AllTube Downloader")
        self.root.geometry("700x520")
        self.dark_mode = True
        self.cancel_download = False
        self.history_file = "download_history.json"
        self.config_file = "user_config.json"

        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="1080p")
        self.playlist_var = tk.BooleanVar()
        self.save_path = tk.StringVar(value=self.load_last_save_path())

        self.set_theme()
        self.create_widgets()

    def load_last_save_path(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f).get("save_path", os.getcwd())
            except:
                pass
        return os.getcwd()

    def save_last_save_path(self):
        with open(self.config_file, 'w') as f:
            json.dump({"save_path": self.save_path.get()}, f)

    def set_theme(self):
        if self.dark_mode:
            self.bg_color = "#1e1e1e"
            self.fg_color = "#ffffff"
            self.entry_bg = "#2e2e2e"
            self.button_bg = "#333333"
            self.button_fg = "#ffffff"
        else:
            self.bg_color = "#ffffff"
            self.fg_color = "#000000"
            self.entry_bg = "#f0f0f0"
            self.button_bg = "#f0f0f0"
            self.button_fg = "#000000"
        self.root.configure(bg=self.bg_color)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.set_theme()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()

    def add_right_click_menu(self, entry_widget):
        menu = tk.Menu(entry_widget, tearoff=0)
        menu.add_command(label="Paste", command=lambda: entry_widget.event_generate("<<Paste>>"))

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        entry_widget.bind("<Button-3>", show_menu)

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        style.configure("TButton", padding=6)
        style.configure("TCombobox", fieldbackground=self.entry_bg, background=self.entry_bg, foreground=self.fg_color)

        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.grid(padx=20, pady=20)

        tk.Label(frame, text="Paste any Video URL:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky='w')
        url_entry = tk.Entry(frame, textvariable=self.url_var, width=60, bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color, relief="flat")
        url_entry.grid(row=0, column=1, pady=5, sticky='ew')
        self.add_right_click_menu(url_entry)

        tk.Label(frame, text="Select Quality:", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, sticky='w')
        ttk.Combobox(frame, textvariable=self.quality_var, values=["360p", "480p", "720p", "1080p"]).grid(row=1, column=1, sticky='ew')

        tk.Checkbutton(frame, text="Download as Playlist", variable=self.playlist_var, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color).grid(row=2, column=1, sticky='w', pady=5)

        tk.Label(frame, text="Save Folder:", bg=self.bg_color, fg=self.fg_color).grid(row=3, column=0, sticky='w')
        path_frame = tk.Frame(frame, bg=self.bg_color)
        path_frame.grid(row=3, column=1, sticky='ew', pady=5)
        path_entry = tk.Entry(path_frame, textvariable=self.save_path, width=45, bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color, relief="flat")
        path_entry.pack(side=tk.LEFT)
        self.add_right_click_menu(path_entry)
        tk.Button(path_frame, text="Browse", command=self.browse_folder, bg=self.button_bg, fg=self.button_fg, relief="flat").pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(frame, length=400, mode='determinate', maximum=100)
        self.progress.grid(row=4, column=0, columnspan=2, pady=10)

        self.status_label = tk.Label(frame, text="", bg=self.bg_color, fg=self.fg_color)
        self.status_label.grid(row=5, column=0, columnspan=2)

        btn_frame = tk.Frame(frame, bg=self.bg_color)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Start Download", command=self.start_download, bg="#28a745", fg="white", relief="flat", padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel Download", command=self.cancel, bg="#dc3545", fg="white", relief="flat", padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Toggle Theme", command=self.toggle_theme, bg="#007bff", fg="white", relief="flat", padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="View History", command=self.show_history, bg="#ffc107", fg="black", relief="flat", padx=10).pack(side=tk.LEFT, padx=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_path.set(folder)
            self.save_last_save_path()

    def start_download(self):
        url = self.url_var.get()
        quality_map = {
            "360p": ["bestvideo[height<=360]+bestaudio", "best[height<=360]"],
            "480p": ["bestvideo[height<=480]+bestaudio", "best[height<=480]"],
            "720p": ["bestvideo[height<=720]+bestaudio", "best[height<=720]"],
            "1080p": ["bestvideo[height<=1080]+bestaudio", "best[height<=1080]", "best"]
        }
        formats = quality_map.get(self.quality_var.get(), ["best"])

        save_dir = self.save_path.get()
        if not url or not save_dir:
            messagebox.showerror("Error", "Please provide both URL and Save Folder.")
            return

        self.cancel_download = False
        self.progress['value'] = 0
        self.status_label.config(text="Downloading...")
        threading.Thread(target=self.try_formats, args=(url, formats, save_dir)).start()

    def try_formats(self, url, formats, save_dir):
        for fmt in formats:
            try:
                self.download_video(url, fmt, save_dir)
                return
            except Exception as e:
                print(f"Format {fmt} failed: {e}")
        messagebox.showerror("Download Failed", "All formats failed.")
        self.status_label.config(text="❌ Error: All formats failed", fg="red")

    def cancel(self):
        self.cancel_download = True
        self.progress.stop()
        self.status_label.config(text="Download cancelled ❌")

    def save_history(self, title, url, file_path):
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        history.append({
            "title": title,
            "url": url,
            "file": file_path,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)

    def show_history(self):
        if not os.path.exists(self.history_file):
            messagebox.showinfo("History", "No history found.")
            return

        with open(self.history_file, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

        history_win = tk.Toplevel(self.root)
        history_win.title("Download History")
        history_win.geometry("600x400")

        text = tk.Text(history_win, wrap="word", bg=self.entry_bg, fg=self.fg_color)
        text.pack(expand=True, fill="both")

        for item in history:
            text.insert("end", f"Title: {item['title']}\nURL: {item['url']}\nSaved to: {item['file']}\nTime: {item['time']}\n{'-'*60}\n")

    def safe_filename(self, title):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in title if c in valid_chars)

    def download_video(self, url, format_code, save_dir):
        ydl_opts = {
            'format': format_code,
            'outtmpl': os.path.join(save_dir, '%(title)s.%(ext)s'),
            'ffmpeg_location': 'ffmpeg',
            'merge_output_format': 'mp4',
            'noplaylist': not self.playlist_var.get(),
            'progress_hooks': [self.hook],
            'quiet': False,
            'verbose': True,
            'postprocessors': [{ 'key': 'FFmpegMetadata' }],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.20 Safari/537.36'
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = self.safe_filename(info.get("title", "video"))
            ext = info.get("ext", "mp4")
            output_file = os.path.join(save_dir, f"{title}.{ext}")
            self.save_history(title, url, output_file)
            self.status_label.config(text=f"Download complete ✅")

    def hook(self, d):
        if self.cancel_download:
            raise yt_dlp.utils.DownloadCancelled("User cancelled the download")

        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', d.get('total_bytes_estimate', 1))
            percent = int(downloaded / total * 100)
            self.progress['value'] = percent
            self.status_label.config(text=f"Downloading... {percent}%")

if __name__ == '__main__':
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
