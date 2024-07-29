import tkinter as tk 
from tkinter import ttk
import time as systime
import pygame
from datetime import datetime
import mysql.connector

from tkinter import messagebox
import sys

database_available = False

class Database():
    def __init__(self):
        if database_available:
            self.db = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user='root',
            password='password',
            database='poromodotimer'
        )

            self.c = self.db.cursor()

    def connect(self):
        try:
            self.db = mysql.connector.connect(
                        host="127.0.0.1",
                        port=3306,
                        user='root',
                        password='password',
                        database='poromodotimer'
                        )
            self.c = self.db.cursor()
            database_available = True
            return True
        except: 
            database_available = False
            return False   
        
    def check_connection(self):
        try:
            self.db.ping(reconnect=True, attempts=3, delay=5)
        except mysql.connector.Error as err:
            print(f"Connection error: {err}")
            self.connect()  # Attempt to reconnect    


    def save_settings(self, sound):
        print(sound)
        self.check_connection()
        prompt = f'UPDATE settings SET sound=%s WHERE id=1'
        self.c.execute(prompt, (sound,))
        self.db.commit()
        

    def save_times(self, startDatetime, endDatetime, foverall):
        prompt = 'INSERT INTO times (sdt, fdt, fat) VALUES (%s, %s, %s)'
        values = (startDatetime, endDatetime, foverall)
        self.c.execute(prompt, values)
        self.db.commit()

    def getData(self):
        prompt = "SELECT * FROM times"  
        self.c.execute(prompt)
        result = self.c.fetchall()
        return result

        

    def comm(self):
        self.db.commit()    

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
        self.overall_time = 0
        self.connect_database()
        

    def connect_database(self):
        self.Database = Database()
        r = self.Database.connect()
        if r:
            print('databse connected your good to go')
            self.databseconn = True
        else:
            messagebox.showerror("databse error", "Could not connect to databse! data will not be saved")  

    

    def main(self):
        self.main_setup()
        self.loop()
        self.root.mainloop()

    def main_setup(self):
        self.root.configure(bg=self.bg_color)
        self.root.title('FOCUS')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_database()
        self.setup_style()
        self.create_notebook()
        self.create_main_window()
        self.create_stats_window()
        self.settings_setup()

    def setup_database(self):
        self.start_datetime = datetime.now()
        data = self.Database.getData()
        print(data)
        print(type(data))

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

        self.notebook.add(self.main_win, text='Timer')
        self.notebook.add(self.stats, text='Statistics')
        self.notebook.add(self.settings, text='Settings')

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.databseconn:
                print('Saving data to databse')
                self.finish_datetime = datetime.now()
                self.Database.save_times(self.start_datetime, self.finish_datetime, self.overall_time)
                self.Database.save_settings(self.soundonoff)    
                self.Database.comm()
            else:
                print('not connected to databse')
            self.root.destroy()
            sys.exit()

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

    def settings_setup(self):       
        self.sound = ttk.Checkbutton(self.settings, text='Sound', command=self.update_settings, style='TCheckbutton')
        self.sound.pack(pady=20)
        

    def update_settings(self):
        if self.i == 1:
            print(self.soundonoff)
            self.i += 1
        else:    
            self.soundonoff = not self.soundonoff
            print(self.soundonoff)


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
        self.root.after(1000, self.loop)

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
    