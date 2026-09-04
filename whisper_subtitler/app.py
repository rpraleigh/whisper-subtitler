import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import stable_whisper
from tkinterdnd2 import DND_FILES, TkinterDnD


class SubtitleApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Video Subtitler (Stable-Whisper)")
        self.root.geometry("520x470")
        self.root.resizable(False, False)

        self.file_path_var = tk.StringVar()
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 15, "pady": 8}

        # Drag & Drop Zone
        self.drop_frame = tk.LabelFrame(
            self.root, text="Source Video", font=("Segoe UI", 9, "bold")
        )
        self.drop_frame.pack(fill="x", **pad)

        self.drop_label = tk.Label(
            self.drop_frame,
            text="Drag and drop a video file here\n— or click to browse —",
            bg="#f0f0f0",
            relief="groove",
            height=4,
            cursor="hand2",
        )
        self.drop_label.pack(fill="x", padx=10, pady=10)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self._on_drop)
        self.drop_label.bind("<Button-1>", lambda e: self._browse_file())

        self.file_display = tk.Label(
            self.drop_frame,
            textvariable=self.file_path_var,
            fg="#555",
            wraplength=480,
            justify="left",
        )
        self.file_display.pack(fill="x", padx=10, pady=(0, 10))

        # Options Box
        settings_frame = tk.LabelFrame(
            self.root, text="Options", font=("Segoe UI", 9, "bold")
        )
        settings_frame.pack(fill="x", **pad)

        # Model Dropdown
        model_row = tk.Frame(settings_frame)
        model_row.pack(fill="x", padx=10, pady=5)
        tk.Label(model_row, text="Model:").pack(side="left")
        self.model_var = tk.StringVar(value="turbo")
        model_dropdown = ttk.Combobox(
            model_row,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "turbo", "large-v3"],
            state="readonly",
            width=12,
        )
        model_dropdown.pack(side="left", padx=10)

        # Max Words Limit
        words_row = tk.Frame(settings_frame)
        words_row.pack(fill="x", padx=10, pady=5)
        tk.Label(words_row, text="Max words per cue:").pack(side="left")
        self.max_words_var = tk.IntVar(value=14)
        words_spin = ttk.Spinbox(
            words_row, from_=6, to=30, textvariable=self.max_words_var, width=5
        )
        words_spin.pack(side="left", padx=10)

        # Sentence Regrouping Checkbox
        self.regroup_var = tk.BooleanVar(value=True)
        cb_regroup = ttk.Checkbutton(
            settings_frame,
            text="Regroup into complete sentences (split by punctuation)",
            variable=self.regroup_var,
        )
        cb_regroup.pack(anchor="w", padx=10, pady=3)

        # Word Highlighting / Karaoke Toggle
        self.highlight_var = tk.BooleanVar(value=False)
        cb_highlight = ttk.Checkbutton(
            settings_frame,
            text="Word highlighting / Karaoke mode",
            variable=self.highlight_var,
        )
        cb_highlight.pack(anchor="w", padx=10, pady=3)

        # Status Message & Process Button
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            self.root, textvariable=self.status_var, fg="#0066cc", anchor="w"
        )
        self.status_label.pack(fill="x", padx=15, pady=(5, 0))

        self.run_btn = ttk.Button(
            self.root, text="Generate Subtitles", command=self._start_thread
        )
        self.run_btn.pack(pady=12)

    def _on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        if not paths:
            return
        path = paths[0]
        if os.path.isfile(path):
            self.file_path_var.set(path)
            self.drop_label.config(text=os.path.basename(path))

    def _browse_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Video Files", "*.mkv *.mp4 *.mov *.avi *.webm"),
                ("All Files", "*.*"),
            ]
        )
        if path:
            self.file_path_var.set(path)
            self.drop_label.config(text=os.path.basename(path))

    def _start_thread(self):
        input_file = self.file_path_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Please select a valid video file first.")
            return

        self.run_btn.config(state="disabled")
        self.status_var.set("Transcribing (this may take several minutes)...")

        t = threading.Thread(target=self._process_transcription, args=(input_file,))
        t.daemon = True
        t.start()

    def _process_transcription(self, input_file):
        try:
            model_name = self.model_var.get()
            max_words = self.max_words_var.get()
            do_regroup = self.regroup_var.get()
            do_highlight = self.highlight_var.get()

            # Load model (automatically utilizes CUDA if torch.cuda.is_available() is True)
            model = stable_whisper.load_model(model_name)
            result = model.transcribe(input_file)

            if do_regroup:
                result.split_by_punctuation([".", "?", "!"])
            if max_words > 0:
                result.split_by_length(max_words=max_words)

            out_path = os.path.splitext(input_file)[0] + ".srt"

            # segment_level=True with word_level=False prevents word-by-word font/color tags
            result.to_srt_vtt(out_path, segment_level=True, word_level=do_highlight)

            self.root.after(0, self._on_success, out_path)
        except Exception as ex:
            self.root.after(0, self._on_failure, str(ex))

    def _on_success(self, out_path):
        self.status_var.set(f"Saved: {os.path.basename(out_path)}")
        self.run_btn.config(state="normal")
        messagebox.showinfo(
            "Complete", f"Subtitles successfully saved to:\n\n{out_path}"
        )

    def _on_failure(self, err_msg):
        self.status_var.set("Error during transcription.")
        self.run_btn.config(state="normal")
        messagebox.showerror("Transcription Failed", err_msg)


def main():
    root = TkinterDnD.Tk()
    app = SubtitleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
