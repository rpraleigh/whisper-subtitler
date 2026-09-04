# **Project Specification: Whisper Subtitler Desktop Application**

A complete blueprint to scaffold, package, test, and publish the whisper-subtitler desktop application to GitHub using Claude Code.

## **1\. Project Overview & Scope**

* **Objective:** Build and package a lightweight, installable desktop GUI application that transcribes video files (.mkv, .mp4, .mov, .avi, .webm) into sentence-based .srt subtitle files without mid-sentence chops or word-highlighting artifacts.  
* **Core Technologies:** Python 3.9+, Tkinter, tkinterdnd2, and stable-ts (Stable-Whisper).  
* **Execution Environment:** Windows CLI environment utilizing GPU acceleration (via PyTorch CUDA) and system-wide FFmpeg.  
* **Entry Point:** A console script command subtitler registered globally in the Python environment.

## **2\. Prerequisites & Dependencies**

### **System Requirements**

* **FFmpeg:** Installed and verified on system PATH (e.g., via winget install Gyan.FFmpeg).  
* **Git & GitHub CLI (gh):** Installed and authenticated for repository creation and pushing.  
* **PyTorch with CUDA (Recommended):** CUDA-enabled PyTorch installed in the active environment:  
  DOS  
  pip install torch torchvision torchaudio \--index-url https://download.pytorch.org/whl/cu124

### **Python Dependencies**

* setuptools\>=61.0  
* stable-ts  
* tkinterdnd2

## **3\. Directory Layout**

Plaintext  
whisper-subtitler/  
├── pyproject.toml  
├── .gitignore  
├── README.md  
└── whisper\_subtitler/  
    ├── \_\_init\_\_.py  
    └── app.py

## **4\. File Contents**

### **File: pyproject.toml**

Ini, TOML  
\[build-system\]  
requires \= \["setuptools\>=61.0"\]  
build-backend \= "setuptools.build\_meta"

\[project\]  
name \= "whisper-subtitler"  
version \= "0.1.0"  
description \= "Lightweight drag-and-drop desktop UI for sentence-based video subtitling using Stable-Whisper."  
readme \= "README.md"  
requires-python \= "\>=3.9"  
license \= { text \= "MIT" }  
dependencies \= \[  
    "stable-ts",  
    "tkinterdnd2"  
\]

\[project.scripts\]  
subtitler \= "whisper\_subtitler.app:main"

### **File: .gitignore**

Code snippet  
\_\_pycache\_\_/  
\*.py\[cod\]  
\*$py.class  
\*.egg-info/  
dist/  
build/  
.venv/  
env/  
\*.srt  
\*.vtt  
\*.mkv  
\*.mp4  
\*.mov  
\*.avi  
\*.webm  
.idea/  
.vscode/

### **File: README.md**

Markdown  
\# Whisper Subtitler

A lightweight drag-and-drop desktop GUI for transcribing video files (\`.mkv\`, \`.mp4\`, \`.mov\`, etc.) and generating clean, sentence-based \`.srt\` subtitles using Stable-Whisper.

\#\# Features  
\- **\*\*Drag-and-Drop Interface:\*\*** Drop video files directly into the window.  
\- **\*\*Natural Sentence Splitting:\*\*** Regroups transcribed segments strictly around terminal punctuation (\`.\`, \`?\`, \`\!\`).  
\- **\*\*Clean Subtitles:\*\*** Disables distracting word-by-word karaoke/highlighting tags.  
\- **\*\*Adjustable Model Selection:\*\*** Choose between \`tiny\`, \`base\`, \`small\`, \`medium\`, \`turbo\`, and \`large-v3\`.  
\- **\*\*Custom Line Length:\*\*** Configure maximum words per subtitle cue to prevent screen crowding.

\#\# System Requirements  
\- Python 3.9+  
\- **\*\*FFmpeg\*\*** available on system \`PATH\` (e.g., \`winget install Gyan.FFmpeg\`).  
\- **\*\*NVIDIA GPU Acceleration (Optional):\*\*** Install PyTorch with CUDA:  
  \`\`\`bash  
  pip install torch torchvision torchaudio \--index-url \[https://download.pytorch.org/whl/cu124\](https://download.pytorch.org/whl/cu124)

## **Installation**

### **Local Editable Install (Development)**

Bash  
git clone \[https://github.com/\](https://github.com/)\<your-username\>/whisper-subtitler.git  
cd whisper-subtitler  
pip install \-e .

### **Install Directly via Pip / GitHub**

Bash  
pip install git+\[https://github.com/\](https://github.com/)\<your-username\>/whisper-subtitler.git

## **Usage**

Run the registered console command from any command prompt:

Bash  
subtitler

\---

\#\#\# File: \`whisper\_subtitler/\_\_init\_\_.py\`

\`\`\`python  
"""Whisper Subtitler Package."""

\_\_version\_\_ \= "0.1.0"

### **File: whisper\_subtitler/app.py**

Python  
import os  
import threading  
import tkinter as tk  
from tkinter import filedialog, messagebox, ttk  
import stable\_whisper  
from tkinterdnd2 import DND\_FILES, TkinterDnD

class SubtitleApp:

  def \_\_init\_\_(self, root):  
    self.root \= root  
    self.root.title("Video Subtitler (Stable-Whisper)")  
    self.root.geometry("520x470")  
    self.root.resizable(False, False)

    self.file\_path\_var \= tk.StringVar()  
    self.\_build\_ui()

  def \_build\_ui(self):  
    pad \= {"padx": 15, "pady": 8}

    \# Drag & Drop Zone  
    self.drop\_frame \= tk.LabelFrame(  
        self.root, text="Source Video", font=("Segoe UI", 9, "bold")  
    )  
    self.drop\_frame.pack(fill="x", \*\*pad)

    self.drop\_label \= tk.Label(  
        self.drop\_frame,  
        text="Drag and drop a video file here\\n— or click to browse —",  
        bg="\#f0f0f0",  
        relief="groove",  
        height=4,  
        cursor="hand2",  
    )  
    self.drop\_label.pack(fill="x", padx=10, pady=10)  
    self.drop\_label.drop\_target\_register(DND\_FILES)  
    self.drop\_label.dnd\_bind("\<\<Drop\>\>", self.\_on\_drop)  
    self.drop\_label.bind("\<Button-1\>", lambda e: self.\_browse\_file())

    self.file\_display \= tk.Label(  
        self.drop\_frame,  
        textvariable=self.file\_path\_var,  
        fg="\#555",  
        wraplength=480,  
        justify="left",  
    )  
    self.file\_display.pack(fill="x", padx=10, pady=(0, 10))

    \# Options Box  
    settings\_frame \= tk.LabelFrame(  
        self.root, text="Options", font=("Segoe UI", 9, "bold")  
    )  
    settings\_frame.pack(fill="x", \*\*pad)

    \# Model Dropdown  
    model\_row \= tk.Frame(settings\_frame)  
    model\_row.pack(fill="x", padx=10, pady=5)  
    tk.Label(model\_row, text="Model:").pack(side="left")  
    self.model\_var \= tk.StringVar(value="turbo")  
    model\_dropdown \= ttk.Combobox(  
        model\_row,  
        textvariable=self.model\_var,  
        values=\["tiny", "base", "small", "medium", "turbo", "large-v3"\],  
        state="readonly",  
        width=12,  
    )  
    model\_dropdown.pack(side="left", padx=10)

    \# Max Words Limit  
    words\_row \= tk.Frame(settings\_frame)  
    words\_row.pack(fill="x", padx=10, pady=5)  
    tk.Label(words\_row, text="Max words per cue:").pack(side="left")  
    self.max\_words\_var \= tk.IntVar(value=14)  
    words\_spin \= ttk.Spinbox(  
        words\_row, from\_=6, to=30, textvariable=self.max\_words\_var, width=5  
    )  
    words\_spin.pack(side="left", padx=10)

    \# Sentence Regrouping Checkbox  
    self.regroup\_var \= tk.BooleanVar(value=True)  
    cb\_regroup \= ttk.Checkbutton(  
        settings\_frame,  
        text="Regroup into complete sentences (split by punctuation)",  
        variable=self.regroup\_var,  
    )  
    cb\_regroup.pack(anchor="w", padx=10, pady=3)

    \# Word Highlighting / Karaoke Toggle  
    self.highlight\_var \= tk.BooleanVar(value=False)  
    cb\_highlight \= ttk.Checkbutton(  
        settings\_frame,  
        text="Word highlighting / Karaoke mode",  
        variable=self.highlight\_var,  
    )  
    cb\_highlight.pack(anchor="w", padx=10, pady=3)

    \# Status Message & Process Button  
    self.status\_var \= tk.StringVar(value="Ready")  
    self.status\_label \= tk.Label(  
        self.root, textvariable=self.status\_var, fg="\#0066cc", anchor="w"  
    )  
    self.status\_label.pack(fill="x", padx=15, pady=(5, 0))

    self.run\_btn \= ttk.Button(  
        self.root, text="Generate Subtitles", command=self.\_start\_thread  
    )  
    self.run\_btn.pack(pady=12)

  def \_on\_drop(self, event):  
    path \= event.data.strip("{}").strip('"')  
    if os.path.isfile(path):  
      self.file\_path\_var.set(path)  
      self.drop\_label.config(text=os.path.basename(path))

  def \_browse\_file(self):  
    path \= filedialog.askopenfilename(  
        filetypes=\[  
            ("Video Files", "\*.mkv \*.mp4 \*.mov \*.avi \*.webm"),  
            ("All Files", "\*.\*"),  
        \]  
    )  
    if path:  
      self.file\_path\_var.set(path)  
      self.drop\_label.config(text=os.path.basename(path))

  def \_start\_thread(self):  
    input\_file \= self.file\_path\_var.get()  
    if not input\_file or not os.path.exists(input\_file):  
      messagebox.showerror("Error", "Please select a valid video file first.")  
      return

    self.run\_btn.config(state="disabled")  
    self.status\_var.set("Transcribing (this may take several minutes)...")

    t \= threading.Thread(target=self.\_process\_transcription, args=(input\_file,))  
    t.daemon \= True  
    t.start()

  def \_process\_transcription(self, input\_file):  
    try:  
      model\_name \= self.model\_var.get()  
      max\_words \= self.max\_words\_var.get()  
      do\_regroup \= self.regroup\_var.get()  
      do\_highlight \= self.highlight\_var.get()

      \# Load model (automatically utilizes CUDA if torch.cuda.is\_available() is True)  
      model \= stable\_whisper.load\_model(model\_name)  
      result \= model.transcribe(input\_file)

      if do\_regroup:  
        result.split\_by\_punctuation(\[".", "?", "\!"\])  
      if max\_words \> 0:  
        result.split\_by\_length(max\_words=max\_words)

      out\_path \= os.path.splitext(input\_file)\[0\] \+ ".srt"

      \# segment\_level=True with word\_level=False prevents word-by-word font/color tags  
      result.to\_srt\_vtt(out\_path, segment\_level=True, word\_level=do\_highlight)

      self.root.after(0, self.\_on\_success, out\_path)  
    except Exception as ex:  
      self.root.after(0, self.\_on\_failure, str(ex))

  def \_on\_success(self, out\_path):  
    self.status\_var.set(f"Saved: {os.path.basename(out\_path)}")  
    self.run\_btn.config(state="normal")  
    messagebox.showinfo(  
        "Complete", f"Subtitles successfully saved to:\\n\\n{out\_path}"  
    )

  def \_on\_failure(self, err\_msg):  
    self.status\_var.set("Error during transcription.")  
    self.run\_btn.config(state="normal")  
    messagebox.showerror("Transcription Failed", err\_msg)

def main():  
  root \= TkinterDnD.Tk()  
  app \= SubtitleApp(root)  
  root.mainloop()

if \_\_name\_\_ \== "\_\_main\_\_":  
  main()

## **5\. Claude Code Execution Prompt**

Paste the block below directly into your Claude Code terminal prompt:

Plaintext  
Please build out the whisper-subtitler repository using the specification provided above:

1\. Create the project directory structure and populate pyproject.toml, .gitignore, README.md, whisper\_subtitler/\_\_init\_\_.py, and whisper\_subtitler/app.py exactly as detailed.  
2\. Install the package locally in editable development mode using:  
   pip install \-e .  
3\. Initialize the git repository, stage all files, and commit:  
   git init  
   git add .  
   git commit \-m "Initial commit: whisper-subtitler desktop application"  
   git branch \-M main  
4\. Use the GitHub CLI to create a public remote repository and push the initial commit:  
   gh repo create whisper-subtitler \--public \--source=. \--push  
5\. Verify that running 'subtitler \--help' or checking the entry point confirms the tool is properly linked.  
