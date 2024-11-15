from Main import Database, Display
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import pandas as pd

df = pd.Timestamp("2019-04-12")
print(df.dayofweek, df.weekday_name)

app = Display()
data = app.seven_day_data()

times, dates = data
print(data)

# Convert time strings to total seconds
time_in_seconds = []
for time_str in times:
    m, s = map(int, time_str.split(':'))
    time_in_seconds.append(m * 60 + s)

# Convert total seconds to minutes
time_in_minutes = [seconds / 60 for seconds in time_in_seconds]

# Convert date strings to datetime objects
dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in dates]

# Create the bar graph with custom colors
plt.figure(figsize=(12, 6), facecolor='#EFEFEF')
plt.bar(dates, time_in_minutes, color='#3F8EFC', edgecolor='#02182B')
plt.xlabel('Date', fontsize=14, color='#070707')
plt.ylabel('Time (minutes)', fontsize=14, color='#070707')
plt.title('Time Data Over Seven Days', fontsize=16, color='#6D696A')
plt.grid(True, color='#6D696A', linestyle='--', linewidth=0.5)
plt.xticks(rotation=45, color='#070707')
plt.yticks(color='#070707')
plt.tight_layout()

# Show the plot
plt.show()