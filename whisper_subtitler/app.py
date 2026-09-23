import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import stable_whisper
from tkinterdnd2 import DND_FILES, TkinterDnD

LANGUAGE_OPTIONS = [
    ("Auto-Detect", "auto"),
    ("Japanese (ja)", "ja"),
    ("Chinese (zh)", "zh"),
    ("English (en)", "en"),
    ("Spanish (es)", "es"),
    ("French (fr)", "fr"),
    ("German (de)", "de"),
    ("Korean (ko)", "ko"),
    ("Italian (it)", "it"),
    ("Russian (ru)", "ru"),
    ("Portuguese (pt)", "pt"),
    ("Czech (cs)", "cs"),
    ("Hindi (hi)", "hi"),
    ("Turkish (tr)", "tr"),
]


class SubtitleApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Video Subtitler (Stable-Whisper)")
    self.root.geometry("560x640")
    self.root.resizable(False, False)

    self.file_path_var = tk.StringVar()
    self._build_ui()

  def _build_ui(self):
    pad = {"padx": 15, "pady": 6}

    # Source File Selection
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
    self.drop_label.pack(fill="x", padx=10, pady=8)
    self.drop_label.drop_target_register(DND_FILES)
    self.drop_label.dnd_bind("<<Drop>>", self._on_drop)
    self.drop_label.bind("<Button-1>", lambda e: self._browse_file())

    self.file_display = tk.Label(
        self.drop_frame,
        textvariable=self.file_path_var,
        fg="#555",
        wraplength=520,
        justify="left",
    )
    self.file_display.pack(fill="x", padx=10, pady=(0, 8))

    # Options Box
    settings_frame = tk.LabelFrame(
        self.root, text="Processing Options", font=("Segoe UI", 9, "bold")
    )
    settings_frame.pack(fill="x", **pad)

    # Row 1: Model
    model_row = tk.Frame(settings_frame)
    model_row.pack(fill="x", padx=10, pady=4)
    tk.Label(model_row, text="Model:", width=22, anchor="w").pack(side="left")
    self.model_var = tk.StringVar(value="large-v3")
    model_dropdown = ttk.Combobox(
        model_row,
        textvariable=self.model_var,
        values=["tiny", "base", "small", "medium", "turbo", "large-v3"],
        state="readonly",
        width=16,
    )
    model_dropdown.pack(side="left")

    # Row 2: Task
    task_row = tk.Frame(settings_frame)
    task_row.pack(fill="x", padx=10, pady=4)
    tk.Label(task_row, text="Task:", width=22, anchor="w").pack(side="left")
    self.task_var = tk.StringVar(value="translate (To English)")
    task_dropdown = ttk.Combobox(
        task_row,
        textvariable=self.task_var,
        values=["transcribe (Original Language)", "translate (To English)"],
        state="readonly",
        width=26,
    )
    task_dropdown.pack(side="left")

    # Row 3: Source Language
    lang_row = tk.Frame(settings_frame)
    lang_row.pack(fill="x", padx=10, pady=4)
    tk.Label(lang_row, text="Source Language:", width=22, anchor="w").pack(
        side="left"
    )
    self.lang_display_names = [label for label, _ in LANGUAGE_OPTIONS]
    self.lang_var = tk.StringVar(value="Japanese (ja)")
    lang_dropdown = ttk.Combobox(
        lang_row,
        textvariable=self.lang_var,
        values=self.lang_display_names,
        state="readonly",
        width=20,
    )
    lang_dropdown.pack(side="left")

    # Row 4: Max Words
    words_row = tk.Frame(settings_frame)
    words_row.pack(fill="x", padx=10, pady=4)
    tk.Label(words_row, text="Max words per cue:", width=22, anchor="w").pack(
        side="left"
    )
    self.max_words_var = tk.IntVar(value=14)
    words_spin = ttk.Spinbox(
        words_row, from_=6, to=30, textvariable=self.max_words_var, width=6
    )
    words_spin.pack(side="left")

    # Row 5: VAD Filter Sensitivity
    vad_row = tk.Frame(settings_frame)
    vad_row.pack(fill="x", padx=10, pady=4)
    self.vad_var = tk.BooleanVar(value=True)
    cb_vad = ttk.Checkbutton(
        vad_row,
        text="Enable VAD (Silence / noise suppression)",
        variable=self.vad_var,
    )
    cb_vad.pack(side="left")

    # Advanced Anti-Hallucination Options
    adv_frame = tk.LabelFrame(
        self.root,
        text="Anti-Hallucination & Formatting",
        font=("Segoe UI", 9, "bold"),
    )
    adv_frame.pack(fill="x", **pad)

    self.regroup_var = tk.BooleanVar(value=True)
    cb_regroup = ttk.Checkbutton(
        adv_frame,
        text="Regroup into complete sentences (split by punctuation)",
        variable=self.regroup_var,
    )
    cb_regroup.pack(anchor="w", padx=10, pady=3)

    self.condition_prev_var = tk.BooleanVar(value=False)
    cb_condition = ttk.Checkbutton(
        adv_frame,
        text="Condition on previous text (Turn OFF to stop repetition loops)",
        variable=self.condition_prev_var,
    )
    cb_condition.pack(anchor="w", padx=10, pady=3)

    self.highlight_var = tk.BooleanVar(value=False)
    cb_highlight = ttk.Checkbutton(
        adv_frame,
        text="Word highlighting / Karaoke mode",
        variable=self.highlight_var,
    )
    cb_highlight.pack(anchor="w", padx=10, pady=3)

    # Status & Execution
    self.status_var = tk.StringVar(value="Ready")
    self.status_label = tk.Label(
        self.root, textvariable=self.status_var, fg="#0066cc", anchor="w"
    )
    self.status_label.pack(fill="x", padx=15, pady=(4, 0))

    self.run_btn = ttk.Button(
        self.root, text="Generate Subtitles", command=self._start_thread
    )
    self.run_btn.pack(pady=10)

  def _on_drop(self, event):
    path = event.data.strip("{}").strip('"')
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
    self.status_var.set("Loading model and transcribing...")

    t = threading.Thread(target=self._process_transcription, args=(input_file,))
    t.daemon = True
    t.start()

  def _process_transcription(self, input_file):
    try:
      model_name = self.model_var.get()
      max_words = self.max_words_var.get()
      do_regroup = self.regroup_var.get()
      do_highlight = self.highlight_var.get()
      use_vad = self.vad_var.get()
      condition_prev = self.condition_prev_var.get()

      is_translation = "translate" in self.task_var.get()
      task = "translate" if is_translation else "transcribe"

      selected_label = self.lang_var.get()
      lang_code = dict(LANGUAGE_OPTIONS).get(selected_label, "auto")
      language = None if lang_code == "auto" else lang_code

      # Load model (CUDA enabled automatically if torch detects GPU)
      model = stable_whisper.load_model(model_name)

      # Transcription options tailored to eliminate noise-induced hallucinations
      transcribe_kwargs = {
          "task": task,
          "condition_on_previous_text": condition_prev,
          "compression_ratio_threshold": 2.2,
          "no_speech_threshold": 0.6,
      }
      if language:
        transcribe_kwargs["language"] = language
      if use_vad:
        transcribe_kwargs["vad"] = True
        transcribe_kwargs["vad_threshold"] = 0.35
        transcribe_kwargs["vad_onnx"] = True

      result = model.transcribe(input_file, **transcribe_kwargs)

      # Sentence formatting & terminal punctuation handling
      if do_regroup:
        result.split_by_punctuation([".", "?", "!", "。", "？", "！"])
      if max_words > 0:
        result.split_by_length(max_words=max_words)

      # File output
      base_path = os.path.splitext(input_file)[0]
      suffix = ".en.srt" if is_translation else ".srt"
      out_path = f"{base_path}{suffix}"

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