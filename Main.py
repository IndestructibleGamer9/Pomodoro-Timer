import tkinter as tk 
from tkinter import ttk
import pygame
from datetime import datetime, date, timedelta
import sqlite3
from tkinter import messagebox
from desktop_notifier import DesktopNotifier, Urgency, Button, ReplyField, DEFAULT_SOUND
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import asyncio

database_available = False

def adapt_datetime(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def convert_datetime(s):
    return datetime.strptime(s.decode('utf-8'), '%Y-%m-%d %H:%M:%S')

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter('DATETIME', convert_datetime)

class Database(): 
    def __init__(self):
        if database_available:
            self.db = sqlite3.connect('UserData.db')
            self.c = self.db.cursor()

    def connect(self):
        try:
            self.db = sqlite3.connect('UserData.db')
            self.c = self.db.cursor()
            database_available = True
            return True
        except: 
            database_available = False
            return False   
        
    def check_connection(self):
        try:
            self.c.execute('SELECT * FROM times')
        except Exception as err:
            print(f"Connection error: {err}")
            self.connect()  # Attempt to reconnect 
            print('attempting to reconnect!')


    def save_settings(self, sound, work, short, long):
        self.check_connection()
        prompt = f'UPDATE settings SET sound=?, work=?, s_brake=?, l_brake=? WHERE id=1'
        self.c.execute(prompt, (sound, work, short, long,))
        self.db.commit()
        

    def save_times(self, startDatetime, endDatetime, foverall):
        prompt = 'INSERT INTO times (start, end, overall) VALUES (?, ?, ?)'
        values = (startDatetime, endDatetime, foverall)
        self.c.execute(prompt, values)
        self.db.commit()

    def getData(self):
        prompt = "SELECT * FROM times"  
        self.c.execute(prompt)
        result = self.c.fetchall()
        return result
    
    def getsettings(self):
        prompt = "SELECT * FROM settings WHERE id=1"  
        self.c.execute(prompt)
        result = self.c.fetchall()
        return result
    
    def comm(self):
        self.db.commit()    

class Display():
    #TODO todolist
    def __init__(self):
        self.root = tk.Tk()
        self.bg_color = '#02182B'
        self.text_color = '#EFEFEF'
        self.accent_color = '#3F8EFC'
        self.secondary_color = '#6D696A'
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.play = False
        self.time = None
        self.period_type = 1
        self.soundonoff = True
        self.countdown_amount = 0
        self.i = 1
        pygame.mixer.init()
        self.overall_time = 0
        self.connect_database()
        self.notifier = DesktopNotifier(app_name='Pomodoro Timer')

    def connect_database(self):
        self.Database = Database()
        r = self.Database.connect()
        if r:
            print('databse connected your good to go')
            self.databseconn = True
        else:
            self.databseconn = False
            messagebox.showerror("databse error", "Could not connect to databse! data will not be saved")  

    

    def main(self):
        self.main_setup()
        self.loop()
        self.root.mainloop()

    def main_setup(self):
        self.root.configure(bg=self.bg_color)
        self.root.title('FOCUS')
        settings =self.Database.getsettings()
        self.time = (int(settings[0][2]) * 60)
        self.setup_database()
        self.setup_style()
        self.create_notebook()
        self.create_main_window()
        self.create_stats_window()
        self.settings_setup()
        

    def setup_database(self):
        self.start_datetime = datetime.now()
        if database_available:
            self.data = self.Database.getData()

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
            # Cancel any pending after callbacks
            for after_id in self.root.tk.call('after', 'info'):
                self.root.after_cancel(after_id)
                
            if self.databseconn:
                self.Database.save_times(self.start_datetime, datetime.now(), self.overall_time)
                try:
                    self.Database.db.close()
                except Exception as e:
                    print('error closing database connection')
            try:
                pygame.mixer.quit()
                pygame.quit()
            except Exception as e:
                print('error closing pygame')
            for widget in self.root.winfo_children():
                widget.destroy()
            self.root.quit()
            self.root.destroy()

    def create_main_window(self):
        #TODO add a progress bar
        self.drop_down = tk.Label(self.main_win, text='', fg=self.text_color, bg=self.bg_color, font=('Arial', 20))
        self.drop_down.pack(pady=(20, 0))
        self.progress = tk.IntVar()
        self.progress.set(0)
        self.progress_bar = ttk.Progressbar(self.main_win, maximum=100, variable=self.progress, style='Horizontal.TProgressbar', length=300)
        self.timer = tk.Label(self.main_win, text=self.format_time(self.time), fg=self.text_color, bg=self.bg_color, font=('Arial', 80, 'bold'))
        self.period = tk.Label(self.main_win, text='WORK', fg=self.accent_color, bg=self.bg_color, font=('Arial', 30, 'bold'))
        self.start_stop = tk.Button(self.main_win, text='START', fg=self.text_color, bg=self.accent_color, font=('Arial', 20, 'bold'), 
                                    command=self.start, relief=tk.FLAT, padx=20, pady=10)
        # Load and display PNG
        self.refresh_im = Image.open('assets/refresh-ccw.png')
        self.arrow_im = Image.open('assets/arrow-right.png')
        self.refresh_ph = ImageTk.PhotoImage(self.refresh_im)
        self.arrow_ph = ImageTk.PhotoImage(self.arrow_im)
        self.refrsh_label = tk.Button(self.main_win, image=self.refresh_ph, command=self.reset)
        self.arrow_button = tk.Button(self.main_win, image=self.arrow_ph, command=self.next)
        self.period.pack(pady=(50, 10))
        self.progress_bar.pack(pady=(0, 20))
        self.timer.pack(pady=30)
        self.start_stop.pack(pady=30)
        self.refrsh_label.pack(side="left", pady=(50, 10))
        self.arrow_button.pack(side="left", pady=(50, 10))

    def create_stats_window(self):
        text = tk.Label(self.stats, text='Overall Time (MM:SS)', fg=self.accent_color, bg=self.bg_color, font=('Arial', 30, 'bold'))  
        self.datalabel = tk.Label(self.stats, text=self.format_time(self.overall_time), fg=self.accent_color, bg=self.bg_color, font=('Arial', 30, 'bold'))

        text.pack()
        self.datalabel.pack()
        
        # Initialize canvas attribute
        self.stats_canvas = None
        self.update_stats_graph()

    def update_stats_graph(self):
        data = self.seven_day_data()
        self.Database.comm()
        times, dates = data
        
        # Convert time strings to total seconds
        time_in_seconds = []
        for time_str in times:
            m, s = map(int, time_str.split(':'))
            time_in_seconds.append(m * 60 + s)
        
        # Convert total seconds to minutes 
        time_in_minutes = [seconds / 60 for seconds in time_in_seconds]
        
        # Add current session time to today's total (index 0)
        time_in_minutes[0] = time_in_minutes[0] + self.overall_time / 60
        
        # Calculate overall time in HH:MM:SS format
        total_seconds = sum(time_in_seconds) + self.overall_time
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        overall_time_str = f'Total Time: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}'
        
        # Ensure dates and time_in_minutes have same length
        if len(dates) != len(time_in_minutes):
            print(f"Warning: Data length mismatch - dates:{len(dates)}, times:{len(time_in_minutes)}")
            min_len = min(len(dates), len(time_in_minutes))
            dates = dates[:min_len]
            time_in_minutes = time_in_minutes[:min_len]

        time_in_minutes[0] + self.overall_time / 60
        # Clear previous graph if it exists
        if self.stats_canvas is not None:
            self.stats_canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(12, 6), facecolor='#EFEFEF')
        ax.bar(dates, time_in_minutes, color='#3F8EFC', edgecolor='#02182B')
        ax.set_xlabel('Date', fontsize=14, color='#070707')
        ax.set_ylabel('Time (minutes)', fontsize=14, color='#070707')
        ax.set_title(f'Time Data Over Seven Days\n{overall_time_str}', fontsize=16, color='#6D696A')
        ax.grid(True, color='#6D696A', linestyle='--', linewidth=0.5)
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, ha='right')

        # Update the canvas
        self.stats_canvas = FigureCanvasTkAgg(fig, master=self.stats)
        self.stats_canvas.draw()
        self.stats_canvas.get_tk_widget().pack()    

    def settings_setup(self):
        #TODO add auto start next session option
        #retrives settings from DB
        settings =self.Database.getsettings()

        # assigns values to tkinter variables
        self.soundonoff = tk.BooleanVar()
        self.work_time = tk.IntVar()
        self.long_break = tk.IntVar()
        self.short_break = tk.IntVar() 
        self.soundonoff.set(settings[0][1])
        self.work_time.set(settings[0][2])
        self.short_break.set(settings[0][3])
        self.long_break.set(settings[0][4])

        # creates widgets and sets them to the variables
        self.sound = ttk.Checkbutton(self.settings, text='Sound', style='TCheckbutton', variable=self.soundonoff)
        self.sound.pack(pady=20)
        self.work_time_changer = tk.Scale(self.settings, variable=self.work_time, from_=20, to=60, orient=tk.HORIZONTAL, label='Work Time (Minutes)', length=200)
        self.work_time_changer.pack(pady=20)
        self.short_breadth_changer = tk.Scale(self.settings, variable=self.short_break, from_=5, to=20, orient=tk.HORIZONTAL, label='Short Break Time (Minutes)', length=200)
        self.short_breadth_changer.pack(pady=20)
        self.long_breadth_changer = tk.Scale(self.settings, variable=self.long_break, from_=20, to=60, orient=tk.HORIZONTAL, label='Long Break Time (Minutes)', length=200)
        self.long_breadth_changer.pack(pady=20)

        self.apply = tk.Button(self.settings, text='Apply', command=self.update_settings, fg=self.text_color, bg=self.accent_color, font=('Arial', 20, 'bold'))
        self.apply.pack(pady=20)
        

    def update_settings(self):
        print('updating settings')
        self.Database.save_settings(self.soundonoff.get(), self.work_time.get(), self.short_break.get(), self.long_break.get())
        self.reset()

    def seven_day_data(self):
        data = self.Database.getData()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        past_week_overall_time = []
        dates = []
        today = date.today()
        
        for i in range(7):
            day = today - timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            dates.append(days[day.weekday()])
            day_data = [entry for entry in data if entry[1].startswith(day_str)]
            
            if day_data:
                overall_time = sum(int(entry[3]) for entry in day_data)
            else:
                overall_time = 0
                
            # Add current session time to today's total
            if i == 0:  # If this is today
                overall_time += self.overall_time
                
            past_week_overall_time.append(self.format_time(overall_time))

        return past_week_overall_time, dates

    def start(self):
        self.play = not self.play
        self.start_stop.config(text='PAUSE' if self.play else 'START')
        self.update_stats_graph()
            

    def loop(self):
        self.datalabel.config(text=self.format_time(self.overall_time))
        if self.play:
            if self.time == 0:
                self.start_stop.config(text='START')
                self.play = False
                self.progress.set(100)  # Set to 100% when complete
                self.finish()
                self.time += 1
            else:
                self.time -= 1
                self.overall_time += 1
                # Calculate and update progress
                total_time = self.work_time.get()*60 if self.id_to_str(self.period_type) == 'Work' else \
                            self.short_break.get()*60 if self.id_to_str(self.period_type) == 'Short Rest' else \
                            self.long_break.get()*60
                progress = ((total_time - self.time) / total_time) * 100
                self.progress.set(progress)
                self.timer.config(text=self.format_time(self.time))
        self.after = self.root.after(1000, self.loop)

    async def send_message(self, ps):
        period_display = 'Start working' if ps == 'Work' else 'Take a break' if ps == 'Short Rest' else 'Have a long rest'
        message_display = 'Come back and start your next work session' if ps == 'Work' else 'Start your short break now, you earned it' if ps == 'Short Rest' else 'Awesome work take a refreshing break you deserve it!'  
        try:
            await self.notifier.send(
                title=period_display,
                message=message_display,
                sound=DEFAULT_SOUND
            )
        except Exception as e:
            print(f"Failed to send notification: {e}")   

    def finish(self):
        self.period_type += 1 
        if self.period_type > 6:
            self.period_type = 1
        ps = self.id_to_str(self.period_type)
        self.time = self.work_time.get()*60 if ps == 'Work' else self.short_break.get()*60 if ps == 'Short Rest' else self.long_break.get()*60
        if ps == 'Long Rest':
            self.message('You completed a full cycle!')
        self.timer.config(text=self.format_time(self.time))    
        asyncio.run(self.send_message(ps))     
        self.period.config(text=ps.upper())
        if self.soundonoff.get():
            self.play_alarm()
        self.reset() 
        print('reseting timer ')   

    def next(self):    
        self.period_type += 1 
        if  self.period_type > 6:
            self.period_type = 1
        ps = self.id_to_str(self.period_type)
        self.time = self.work_time.get()*60 if ps == 'Work' else self.short_break.get()*60 if ps == 'Short Rest' else self.long_break.get()*60
        self.timer.config(text=self.format_time(self.time)) 
        self.start_stop.config(text='START')
        self.play = False
        self.period.config(text=ps.upper())

    def reset(self):
        ps = self.id_to_str(self.period_type)
        self.time = self.work_time.get()*60 if ps == 'Work' else self.short_break.get()*60 if ps == 'Short Rest' else self.long_break.get()*60
        self.timer.config(text=self.format_time(self.time)) 
        self.start_stop.config(text='START')
        self.play = False
        self.period.config(text=ps.upper())
        self.progress.set(0)        

    def format_time(self, seconds):
        min, sec = divmod(seconds, 60)
        return f'{min:02d}:{sec:02d}'

    def message(self, message, duration=5000):
        self.drop_down.config(text=message, bg=self.accent_color)
        self.message_after = self.root.after(duration, self.clear_message)

    def clear_message(self):
        self.drop_down.config(text='', bg=self.bg_color)    

    def id_to_str(self, period):
        id = {1: 'Work', 2: 'Short Rest', 3: 'Work', 4: 'Short Rest', 5: 'Work', 6: 'Long Rest'}
        return id[period]

    def play_alarm(self):
        #TODO new alarms?
        if self.soundonoff:
            try:
                pygame.mixer.music.load('Alarm.mp3')
                pygame.mixer.music.play()
            except pygame.error as e:
                print(f"Error playing sound: {e}")

if __name__ == "__main__":
    app = Display()
    app.main()
    