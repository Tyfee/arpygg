import mido
import time
import sys
from mido import Message
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import json



root = tk.Tk()
root.title("Arpygg")
root.geometry("370x400")
root.resizable(False, False)

root.configure(background="white")
menubar = tk.Menu()
delay = tk.DoubleVar()
velocity = tk.IntVar()

current_cr = tk.StringVar()
current_cr.set("black")
delay.set(1) 
velocity.set(64)


all_midi_outputs = mido.get_output_names()

port_name = 'none'
loop = False
playing_notes = []
active_notes = []
current_scale = 4
playing = tk.BooleanVar()
playing.set(False)


notes = [f'C{current_scale}',
 f'D{current_scale}', 
 f'E{current_scale}',
 f'F{current_scale}',
 f'G{current_scale}',
 f'A{current_scale}', 
 f'B{current_scale}']

accidentals = [f'C#{current_scale}',
 f'D#{current_scale}', 
 f'F#{current_scale}',
 f'G#{current_scale}',
 f'A#{current_scale}'
 ]

note_map = {
    'C0': 12, 'C#0': 13, 'D0': 14, 'D#0': 15, 'E0': 16, 'F0': 17,
    'F#0': 18, 'G0': 19, 'G#0': 20, 'A0': 21, 'A#0': 22, 'B0': 23,
    'C1': 24, 'C#1': 25, 'D1': 26, 'D#1': 27, 'E1': 28, 'F1': 29,
    'F#1': 30, 'G1': 31, 'G#1': 32, 'A1': 33, 'A#1': 34, 'B1': 35,
    'C2': 36, 'C#2': 37, 'D2': 38, 'D#2': 39, 'E2': 40, 'F2': 41,
    'F#2': 42, 'G2': 43, 'G#2': 44, 'A2': 45, 'A#2': 46, 'B2': 47,
    'C3': 48, 'C#3': 49, 'D3': 50, 'D#3': 51, 'E3': 52, 'F3': 53,
    'F#3': 54, 'G3': 55, 'G#3': 56, 'A3': 57, 'A#3': 58, 'B3': 59,
    'C4': 60, 'C#4': 61, 'D4': 62, 'D#4': 63, 'E4': 64, 'F4': 65,
    'F#4': 66, 'G4': 67, 'G#4': 68, 'A4': 69, 'A#4': 70, 'B4': 71,
    'C5': 72, 'C#5': 73, 'D5': 74, 'D#5': 75, 'E5': 76, 'F5': 77,
    'F#5': 78, 'G5': 79, 'G#5': 80, 'A5': 81, 'A#5': 82, 'B5': 83,
    'C6': 84, 'C#6': 85, 'D6': 86, 'D#6': 87, 'E6': 88, 'F6': 89,
    'F#6': 90, 'G6': 91, 'G#6': 92, 'A6': 93, 'A#6': 94, 'B6': 95,
    'C7': 96, 'C#7': 97, 'D7': 98, 'D#7': 99, 'E7': 100, 'F7': 101,
    'F#7': 102, 'G7': 103, 'G#7': 104, 'A7': 105, 'A#7': 106, 'B7': 107,
    'C8': 108
}

def add(note):
    if len(playing_notes) < 7:
      playing_notes.append(note)
      active_notes.append(note)
      update_rectangles()
   
def take(note):
   active_notes.remove(note) if note in active_notes else print('not there')
   update_rectangles()

def update_button_state():
    
    button.config(state="normal" if not playing.get() else "disabled")
    button2.config(state="normal" if playing.get() else "disabled")


def midi_thread_function():
   global playing
   velocity_value = int(velocity.get())
   delay_value = float(delay.get())
   if port_name != 'none':
    if len(playing_notes) > 0:
     with mido.open_output(port_name) as port:
        while playing.get():  # Add your loop condition here
            for notee in playing_notes:
                note_on = Message('note_on', note=note_map[notee], velocity=velocity_value)
                port.send(note_on)
                active_notes.append(notee)
                update_rectangles()  # Assuming you have a function to update visuals
                print(active_notes)
                time.sleep(delay_value)

                note_off = Message('note_off', note=note_map[notee])
                active_notes.remove(notee) if notee in active_notes else print('not there')
                update_rectangles()  # Assuming you have a function to update visuals
                print(notee)
                port.send(note_off)

            if not loop:
                break
    else:
       messagebox.showerror("Error", "No notes have been set!")
   else:
      messagebox.showerror("Error", "Select an output port!")
   playing.set(False)
   update_button_state()

def start_midi_thread():
    global playing
    playing.set(True)
    midi_thread = threading.Thread(target=midi_thread_function)
    midi_thread.start()
    print("MIDI Thread started!")
    update_button_state()

def stop_midi_thread():
    global loop
    global playing
    playing.set(False)
    update_button_state()
    midi_thread.join()
    print("MIDI Thread joined!")
  
def on_space(event):
  global playing
  start_midi_thread() if not playing.get() else stop_midi_thread()


def toggle_loop():
  global loop
  loop = not loop
  button3.config(text=f"LOOP: {'YES' if loop else 'NO'}")
  print('looping changed')

def on_combobox_select(event):
    global port_name
    selected_value = combobox.get()
    print(f'Selected value: {selected_value}')
    port_name = selected_value
    # Set the focus back to the root window (or any other widget of your choice)
    root.focus_set()


def save_preset():
    initial_dir = os.path.join(os.getcwd(), 'presets')  # Set the initial directory
    file_path = filedialog.asksaveasfilename(
        initialdir=initial_dir,
        defaultextension=".arp",
        filetypes=[("ARP files", "*.arp")]
    )
    if file_path:
        with open(file_path, 'w') as f:
            json.dump({'playing_notes': playing_notes, 'loop': loop, 'delay': delay.get(), 'velocity': velocity.get()}, f)



def load_preset():
   global playing_notes
   global loop
   file_path = filedialog.askopenfilename(title="Select File", filetypes=[("Arpygg presets", "*.arp"), ("All files", "*.*")])
   if file_path:
    
    root.title(f"Arpygg - {os.path.basename(file_path)}")
    with open(file_path, 'r') as f:
     data = json.load(f)
     playing_notes = data['playing_notes']
     loop = data['loop']
     delayy = data['delay']
     velocityy = data['velocity']
     delay.set(delayy)
     velocity.set(velocityy)
     active.config(text=' '.join(playing_notes)) 
     button3.config(text=f"LOOP: {'YES' if loop else 'NO'}")


def change_theme(color):
    root.configure(background=color)
    canvas.config(bg=color)
    
    if color == 'black':
      bottom_right_element.config(fg='white', bg="black")
      temp_label.config(foreground='white', background="black")
      temp_label1.config(foreground='white', background="black")
      active.config(fg='white', bg="black")
      spin_temp.config(background="white")
      z_label.config(fg="white", background="black")
      x_label.config(fg="white", background="black")
      oct_label.config(fg="white", background="black")
      button.config(background="SystemButtonFace", borderwidth=1, highlightthickness=1)
      button2.config(background="SystemButtonFace", borderwidth=1, highlightthickness=1)
      button3.config(background="SystemButtonFace", borderwidth=1, highlightthickness=1)
    elif color == 'white': 
      bottom_right_element.config(fg='black', bg="white")
      temp_label.config(foreground='black', background="white")
      temp_label1.config(foreground='black', background="white")
      active.config(fg='black', bg="white") 
      z_label.config(fg="black", background="white")
      x_label.config(fg="black", background="white")
      oct_label.config(fg="black", background="white")
      button.config(background="SystemButtonFace", borderwidth=1, highlightthickness=1)
      button2.config(background="SystemButtonFace", borderwidth=1, highlightthickness=1)
      button3.config(background="SystemButtonFace", borderwidth=1, highlightthickness=1)
    elif color == '#B5BCFF': 
      bottom_right_element.config(fg='black', bg=color)
      temp_label.config(foreground='black', background=color)
      temp_label1.config(foreground='black', background=color)
      z_label.config(fg="black", background=color)
      x_label.config(fg="black", background=color)
      oct_label.config(fg="black", background=color)
      active.config(fg='black', bg=color, borderwidth=0, highlightthickness=0) 
      button.config(background="#FFD4F1", borderwidth=1, highlightthickness=1)
      button2.config(background="#FFD4F1", borderwidth=1, highlightthickness=1)
      button3.config(background="#FFD4F1", borderwidth=1, highlightthickness=1)


file_menu = tk.Menu(menubar, tearoff=False)
menubar.add_cascade(menu=file_menu, label="File")
file_menu.add_command(
    label="Save as preset",
    accelerator="Ctrl+S",
    command=save_preset
)
file_menu.add_command(
    label="Load preset",
    accelerator="Ctrl+O",
    command=load_preset
)

themes_menu = tk.Menu(menubar, tearoff=False)
menubar.add_cascade(menu=themes_menu, label="Theme")

themes_menu.add_command(
  label="Light",
  command=lambda: change_theme('white')
)
themes_menu.add_command(
  label="Dark",
  command=lambda: change_theme('black')
)
themes_menu.add_command(
  label="Pastel",
  command=lambda: change_theme('#B5BCFF')
)

root.config(menu=menubar)


selected_value = tk.StringVar()

combobox = ttk.Combobox(root,  textvariable=selected_value, width=40, state="readonly")
combobox.bind('<<ComboboxSelected>>', on_combobox_select)

combobox['values'] = all_midi_outputs  # Set the values for the dropdown
combobox.set('MIDI Output') 
combobox.pack(pady=10)



active = tk.Label(root, text=' '.join(active_notes), font=("Helvetica", 20), fg="black", bg="white")
active.pack(side=tk.TOP)


def on_backspace(event):
  playing_notes.pop()
  active.config(text=' '.join(playing_notes))



def update_rectangles():
    canvas.delete("all")  # Clear the canvas

    for index, note in enumerate(notes):
       x1 = 85 + (index * 28)
       x2 = x1 + 30  # Assuming each rectangle has a width of 30
       y1, y2 = 50, 150

       fill_color = "red" if note in active_notes else "white"
       canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color)
       #canvas.create_text((x1 + x2) // 2, (y1 + y2 + 50) // 2, text=note, fill="black")

    for index,note in enumerate(accidentals):
       if "C#" in note:
        x1 = 102
       elif "D#" in note:
        x1 = 132
       elif "F#" in note:
        x1 = 187
       elif "G#" in note:
        x1 = 215 
       elif "A#" in note:
        x1 = 243 
       else:
        x1 = 110 + (index * 42)
       x2 = x1 + 20  # Assuming each rectangle has a width of 30
       y1, y2 = 50, 100

       fill_color = "red" if note in active_notes else "black"
       canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color)
       # canvas.create_text((x1 + x2) // 2, (y1 + y2 ) // 2, text=note, fill="white", font=('Helvetica', 7))





def on_key_press(event):
  global current_scale
  global notes
  global accidentals
  match event.char:

    case 'a'|'A':
      add(f'C{current_scale}')    
    case 's'|'S':
     add(f'D{current_scale}')    
    case 'd'|'D':
       add(f'E{current_scale}')    
    case 'f'|'F':
         add(f'F{current_scale}')    
    case 'g'|'G':
      add(f'G{current_scale}')    
    case 'h'|'H':
        add(f'A{current_scale}')    
    case 'j'|'J':
        add(f'B{current_scale}')    
    case 'w'|'W':
        add(f'C#{current_scale}')   
    case 'e'|'E':
        add(f'D#{current_scale}') 
    case 't'|'T':
        add(f'F#{current_scale}')      
    case 'y'|'Y':
        add(f'G#{current_scale}')  
    case 'u'|'U':
        add(f'A#{current_scale}')        
    case 'z'|'Z': 
     if current_scale > 0: 
      current_scale -= 1
      oct_label.config(text="Octave: " + str(current_scale))
    case 'x'|'X': 
     if current_scale < 7:  
      current_scale += 1
      oct_label.config(text="Octave: " + str(current_scale))

  notes = [f'C{current_scale}',
 f'D{current_scale}', 
 f'E{current_scale}',
 f'F{current_scale}',
 f'G{current_scale}',
 f'A{current_scale}', 
 f'B{current_scale}']
  active.config(text=' '.join(playing_notes))  
  print(f"Key: {event.char}")

  accidentals = [f'C#{current_scale}',
   f'D#{current_scale}', 
   f'F#{current_scale}',
   f'G#{current_scale}',
   f'A#{current_scale}'
   ]


def on_key_release(event):
 global current_scale
 match event.char:
    case 'a'|'A':
     take(f'C{current_scale}')
    case 's'|'S':
     take(f'D{current_scale}')
    case 'd'|'D':
     take(f'E{current_scale}')
    case 'f'|'F':
     take(f'F{current_scale}')
    case 'g'|'G':
     take(f'G{current_scale}')
    case 'h'|'H':
     take(f'A{current_scale}')
    case 'j'|'J':
     take(f'B{current_scale}')
    case 'w'|'W':
     take(f'C#{current_scale}')
    case 'e'|'E':
     take(f'D#{current_scale}')
    case 't'|'T':
     take(f'F#{current_scale}')
    case 'y'|'Y':
     take(f'G#{current_scale}')
    case 'u'|'U':
     take(f'A#{current_scale}')

 print(f"Key: {event.char} released")


canvas = tk.Canvas(root, width=400, height=200, bg='white', borderwidth=0, highlightthickness=0)
canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

update_rectangles()



# select the delay between notes
temp_label1 = ttk.Label(text="Delay:", foreground="black", background="white")
temp_label1.place(x=20, y=320, width=100)
spin_temp = ttk.Spinbox()
spin_temp = ttk.Spinbox(from_=0, to=5, increment=0.1, state="readonly", textvariable=delay)
spin_temp.place(x=58, y=320, width=50)

#select the note velocity

temp_label = ttk.Label(text="Velocity:", foreground="black", background="white")
temp_label.place(x=150, y=320, width=100)
spin_temp = ttk.Spinbox()
spin_temp = ttk.Spinbox(from_=0, to=127, increment=1.0,textvariable=velocity, state="readonly")
spin_temp.place(x=200, y=320, width=50)

z_label = tk.Label(text="◀ z", foreground="black", background="white", font=("Helvetica", 15))
z_label.place(x=0, y=200)
x_label = tk.Label(text="x ▶", foreground="black", background="white", font=("Helvetica", 15))
x_label.place(x=337, y=200)

oct_label = tk.Label(text="Octave: " + str(current_scale), foreground="black", background="white", font=("Helvetica", 10))
oct_label.place(x=151, y=250)

button = tk.Button(root, text="▶ PLAY", command=start_midi_thread, state="normal" if not playing.get() else "disabled")
button.pack(side=tk.LEFT, padx=4)
button2 = tk.Button(root, text="■ STOP", command=stop_midi_thread,  state="normal" if playing.get() else "disabled")
button2.pack(side=tk.LEFT, padx=4)

button3 = tk.Button(root, text=f"LOOP: {'YES' if loop else 'NO'}", command=toggle_loop)
button3.pack(side=tk.LEFT, padx=4)

bottom_right_element = tk.Label(root, text="Arpygg v0.1", foreground="black", background="white")
bottom_right_element.pack(side=tk.RIGHT, anchor=tk.SE, padx=10, pady=10)

root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)
root.bind("<BackSpace>", on_backspace)
root.bind("<space>", on_space)
root.iconbitmap("icon.ico")
root.mainloop()

