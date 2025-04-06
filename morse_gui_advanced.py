import numpy as np
import sounddevice as sd
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import speech_recognition as sr

# Morse Code Dictionary
morse_dict = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', '0': '-----', ' ': '/'
}

# Morse Code Sound Properties
fs = 8000
freq = 800
dot_length = 0.1
dash_length = dot_length * 3

# Convert Text to Morse Code
def text_to_morse(text):
    text = text.upper()
    return ' '.join(morse_dict[char] for char in text if char in morse_dict)

# Generate Morse Code Signal
def morse_to_signal(morse_code):
    signal = np.array([])
    for char in morse_code:
        if char == '.':
            tone = np.sin(2 * np.pi * freq * np.linspace(0, dot_length, int(fs * dot_length)))
        elif char == '-':
            tone = np.sin(2 * np.pi * freq * np.linspace(0, dash_length, int(fs * dash_length)))
        else:
            tone = np.zeros(int(fs * dot_length))
        signal = np.concatenate((signal, tone, np.zeros(int(fs * dot_length))))
    return signal

# Play Morse Code Signal
def play_signal(signal):
    sd.play(signal, fs)
    sd.wait()

# Animate Morse Code Blinking Light
def animate_morse(morse_code):
    for char in morse_code:
        if char in ['.', '-']:
            light_canvas.itemconfig(light, fill="yellow")
            root.update()
            root.after(300 if char == '.' else 900, lambda: light_canvas.itemconfig(light, fill="black"))
        root.after(200)

# Update Morse Code Display with Scrolling Effect
def update_morse_display(morse_code):
    label_morse.configure(text="Morse Code: " + morse_code)
    for i in range(len(morse_code)):
        label_morse.configure(text="Morse Code: " + morse_code[:i+1])
        root.update()
        root.after(150)

# Convert, Play & Show Visualization
def convert_and_play():
    text = entry.get()
    if not text:
        status_label.configure(text="Enter text first!", text_color="red")
        return
    
    morse_code = text_to_morse(text)
    update_morse_display(morse_code)

    morse_signal = morse_to_signal(morse_code)
    
    play_signal(morse_signal)
    animate_morse(morse_code)

    # Update progress bar
    progress_bar.start(10)
    root.after(2000, lambda: progress_bar.stop())

    # Plot Signal Graph
    ax.clear()
    ax.plot(morse_signal[:2000], color='cyan')
    ax.set_title("Morse Code Signal")
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.grid()
    canvas.draw()

# Convert Speech to Text and then to Morse

def speech_to_morse():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        status_label.configure(text="Listening... Speak now!", text_color="yellow")
        root.update()
        
        try:
            # Listen with a timeout (max wait time before speaking) and phrase time limit
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)  
            
            # Convert Speech to Text
            text = recognizer.recognize_google(audio).upper()
            entry.delete(0, tk.END)  # Clear previous text
            entry.insert(0, text)  # Insert recognized text into entry field
            
            status_label.configure(text="Recognized: " + text, text_color="green")
            convert_and_play()  # Convert and play Morse code
            
        except sr.WaitTimeoutError:
            status_label.configure(text="No speech detected. Try again!", text_color="red")
        except sr.UnknownValueError:
            status_label.configure(text="Couldn't understand the speech!", text_color="red")
        except sr.RequestError:
            status_label.configure(text="Speech recognition service error!", text_color="red")

# CustomTkinter Modern UI Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Morse Code Encoder-Decoder")
root.geometry("600x700")

# Background Frame
bg_frame = ctk.CTkFrame(root, fg_color=("black", "#222222"), corner_radius=20)
bg_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Title
title_label = ctk.CTkLabel(bg_frame, text="🔵 Morse Code Encoder", font=("Arial", 20, "bold"), text_color="cyan")
title_label.pack(pady=15)

# Entry Field
entry = ctk.CTkEntry(bg_frame, width=350, placeholder_text="Enter text...", font=("Arial", 14))
entry.pack(pady=10)

# Convert Button
convert_button = ctk.CTkButton(bg_frame, text="Convert & Play", font=("Arial", 14), command=convert_and_play)
convert_button.pack(pady=10)

# Mic Button for Speech Input
mic_button = ctk.CTkButton(bg_frame, text="🎤 Speak & Convert", font=("Arial", 14), fg_color="red", command=speech_to_morse)
mic_button.pack(pady=10)

# Morse Code Display
label_morse = ctk.CTkLabel(bg_frame, text="Morse Code: ", font=("Arial", 14))
label_morse.pack(pady=10)

# Light Indicator for Morse Code Animation
light_canvas = tk.Canvas(bg_frame, width=80, height=80, bg="#222222", highlightthickness=0)
light_canvas.pack(pady=10)
light = light_canvas.create_oval(10, 10, 70, 70, fill="black")

# Progress Bar
progress_bar = ttk.Progressbar(bg_frame, length=300, mode='indeterminate')
progress_bar.pack(pady=10)

# Matplotlib Graph
fig, ax = plt.subplots(figsize=(5, 2), facecolor="#222222")
ax.set_facecolor("#222222")
ax.spines['bottom'].set_color("white")
ax.spines['top'].set_color("white")
ax.spines['right'].set_color("white")
ax.spines['left'].set_color("white")
ax.tick_params(colors="white")

canvas = FigureCanvasTkAgg(fig, master=bg_frame)
canvas.get_tk_widget().pack(pady=10)

# Status Label
status_label = ctk.CTkLabel(bg_frame, text="", font=("Arial", 12))
status_label.pack(pady=10)

# Run GUI
root.mainloop()
