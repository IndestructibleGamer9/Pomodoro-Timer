import tkinter as tk 
from tkinter import ttk
import time as systime
import threading
import pygame
from DataHandle import DataControl

class Display():
    def __init__(self):
        self.root = tk.Tk()
        self.bg_color = '#02182B'
        self.text_color = '#EFEFEF'
        self.accent_color = '#3F8EFC'
        self.secondary_color = '#6D696A'
        self.play = False
        self.time = 1200
        self.period_type = 1
        self.soundonoff = True
        self.i = 1
        pygame.mixer.init()
        self.database = DataControl()
        self.overall_time = 0
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def main(self):
        self.main_setup()
        self.loop()
        self.root.mainloop()

    def main_setup(self):
        self.root.configure(bg=self.bg_color)
        self.root.title('FOCUS')
        self.open_database()
        self.setup_style()
        self.create_notebook()
        self.create_main_window()
        self.create_stats_window()
        self.settings_setup()
        self.create_todo_window()  # Add this line

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TFrame', background=self.bg_color)
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.secondary_color, foreground=self.text_color, borderwidth=0, padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', self.accent_color)])
        style.layout('TNotebook', [('TNotebook.client', {'sticky': 'nswe'})])
        
        style.configure('TCheckbutton', background=self.bg_color, foreground=self.text_color)
        style.map('TCheckbutton', background=[('active', self.secondary_color)])

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root, style='TNotebook')
        self.notebook.pack(expand=True, fill='both', padx=20, pady=20)

        self.main_win = ttk.Frame(self.notebook, style='TFrame')
        self.stats = ttk.Frame(self.notebook, style='TFrame')
        self.settings = ttk.Frame(self.notebook, style='TFrame')
        self.todo_win = ttk.Frame(self.notebook, style='TFrame')  # New todo tab

        self.notebook.add(self.main_win, text='Timer')
        self.notebook.add(self.stats, text='Statistics')
        self.notebook.add(self.settings, text='Settings')
        self.notebook.add(self.todo_win, text='To-Do')  # Add the new tab

    def create_main_window(self):
        self.drop_down = tk.Label(self.main_win, text='', fg=self.text_color, bg=self.bg_color, font=('Arial', 20))
        self.drop_down.pack(pady=(20, 0))

        self.timer = tk.Label(self.main_win, text=self.format_time(self.time), fg=self.text_color, bg=self.bg_color, font=('Arial', 80, 'bold'))
        self.period = tk.Label(self.main_win, text='WORK', fg=self.accent_color, bg=self.bg_color, font=('Arial', 30, 'bold'))
        self.start_stop = tk.Button(self.main_win, text='START', fg=self.text_color, bg=self.accent_color, font=('Arial', 20, 'bold'), 
                                    command=self.start, relief=tk.FLAT, padx=20, pady=10)

        self.period.pack(pady=(50, 10))
        self.timer.pack(pady=30)
        self.start_stop.pack(pady=30)

    def create_stats_window(self):
        text = tk.Label(self.stats, text='Overall Time (MM:SS)', fg=self.accent_color, bg=self.bg_color, font=('Arial', 30, 'bold'))  
        self.datalabel = tk.Label(self.stats, text=self.format_time(self.overall_time), fg=self.accent_color, bg=self.bg_color, font=('Arial', 30, 'bold'))

        text.pack()
        self.datalabel.pack()

    def create_todo_window(self):
        todo_frame = ttk.Frame(self.todo_win, style='TFrame')
        todo_frame.pack(expand=True, fill='both', padx=20, pady=20)

        todo_label = tk.Label(todo_frame, text="To-Do List", fg=self.accent_color, bg=self.bg_color, font=('Arial', 20, 'bold'))
        todo_label.pack(pady=(0, 10))

        # Create a frame for the todo list
        list_frame = ttk.Frame(todo_frame, style='TFrame')
        list_frame.pack(expand=True, fill='both')

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a listbox for todos
        self.todo_listbox = tk.Listbox(list_frame, bg=self.bg_color, fg=self.text_color,
                                    selectbackground=self.accent_color, font=('Arial', 12),
                                    yscrollcommand=scrollbar.set)
        self.todo_listbox.pack(expand=True, fill='both')
        scrollbar.config(command=self.todo_listbox.yview)

        # Entry field and button to add new todos
        entry_frame = ttk.Frame(todo_frame, style='TFrame')
        entry_frame.pack(fill='x', pady=(10, 0))

        self.todo_entry = tk.Entry(entry_frame, bg=self.secondary_color, fg=self.text_color,
                                insertbackground=self.text_color, font=('Arial', 12))
        self.todo_entry.pack(side=tk.LEFT, expand=True, fill='x')

        add_button = tk.Button(entry_frame, text="Add", fg=self.text_color, bg=self.accent_color,
                            font=('Arial', 12), command=self.add_todo)
        add_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Button to remove completed todos
        remove_button = tk.Button(todo_frame, text="Remove Completed", fg=self.text_color,
                                bg=self.accent_color, font=('Arial', 12), command=self.remove_completed)
        remove_button.pack(pady=(10, 0))

        # Load existing todos
        self.load_todos()

def add_todo(self):
    todo = self.todo_entry.get()
    if todo:
        self.todo_listbox.insert(tk.END, todo)
        self.todo_entry.delete(0, tk.END)
        self.save_todos()

def remove_completed(self):
    completed = self.todo_listbox.curselection()
    for index in reversed(completed):
        self.todo_listbox.delete(index)
    self.save_todos()

def load_todos(self):
    todos = self.database.get_todos()
    for todo in todos:
        self.todo_listbox.insert(tk.END, todo)

def save_todos(self):
    todos = self.todo_listbox.get(0, tk.END)
    self.database.save_todos(todos)    

    def settings_setup(self):
        finding = self.database.get_setting()
        print(finding[0])
        print(type(finding[0]))
        if finding[0] == '1':
            self.soundonoff = True
        elif finding[0] == '2':
            self.soundonoff = False
        else:
            print('error in settings setup')        
        self.sound = ttk.Checkbutton(self.settings, text='Sound', command=self.update_settings, style='TCheckbutton')
        self.sound.pack(pady=20)
        
        # Set the checkbutton state based on the database value
        if self.soundonoff:
            self.sound.state(['selected'])
        else:
            self.sound.state(['!selected'])

    def update_settings(self):
        if self.i == 1:
            print(self.soundonoff)
            self.i += 1
        else:    
            self.soundonoff = not self.soundonoff
            print(self.soundonoff)

    def open_database(self):
        self.database.connect()


    def start(self):
        self.play = not self.play
        self.start_stop.config(text='PAUSE' if self.play else 'START')
        if self.play:
            self.alarm = False

    def loop(self):
        self.datalabel.config(text=self.format_time(self.overall_time))
        if self.play:
            if self.time == 0:
                self.play = False
                self.finish()
                self.time += 1
            self.time -= 1 
            self.overall_time += 1
            self.timer.config(text=self.format_time(self.time))
        else:
            self.overall_time += 1
        self.root.after(1, self.loop)

    def finish(self):
        self.period_type += 1 
        ps = self.id_to_str(self.period_type)
        self.time = 1200 if ps == 'Work' else 300 if ps == 'Short Rest' else 1500
        if ps == 'Long Rest':
            self.message('You completed a full cycle!')
        self.timer.config(text=self.format_time(self.time)) 
        self.start_stop.config(text='START')
        self.play = False
        self.period.config(text=ps.upper())
        self.play_alarm()

    def format_time(self, seconds):
        min, sec = divmod(seconds, 60)
        return f'{min:02d}:{sec:02d}'

    def message(self, message, duration=5000):
        self.drop_down.config(text=message, bg=self.accent_color)
        self.root.after(duration, self.clear_message)

    def clear_message(self):
        self.drop_down.config(text='', bg=self.bg_color)    

    def close(self):
        print('finalising')
        self.save_todos()  # Add this line
        self.database.close(self.format_time(self.overall_time), self.soundonoff)  
        self.root.destroy() 

    def id_to_str(self, period):
        id = {1: 'Work', 2: 'Short Rest', 3: 'Work', 4: 'Short Rest', 5: 'Work', 6: 'Long Rest'}
        return id[period]

    def play_alarm(self):
        if self.soundonoff:
            try:
                pygame.mixer.music.load('Alarm.mp3')
                pygame.mixer.music.play()
            except pygame.error as e:
                print(f"Error playing sound: {e}")

if __name__ == "__main__":
    app = Display()
    app.main()