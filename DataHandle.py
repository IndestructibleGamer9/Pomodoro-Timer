import mysql.connector
from datetime import datetime

USERNAME = 'TESTING'

class DataControl():
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Blue7afl",  # Replace with your MySQL password
                database="AIO_app"  # Replace with your database name
            )
            self.cursor = self.connection.cursor()

            # Create tables if they don't exist
            self.create_tables()

            # Find the last ID and create a new one
            self.cursor.execute("SELECT MAX(ID) FROM pomodoro_data")
            result = self.cursor.fetchone()
            last_id = result[0] if result[0] is not None else 0
            new_id = last_id + 1

            # Add new entry
            insert_query = """
            INSERT INTO pomodoro_data (ID, LogOn, Active)
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(insert_query, (new_id, datetime.now(), True))
            self.connection.commit()

        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return

    def create_tables(self):
        create_pomodoro_table = """
        CREATE TABLE IF NOT EXISTS pomodoro_data (
            ID INT PRIMARY KEY,
            LogOn DATETIME,
            LogOff DATETIME,
            PromoTime INT,
            Active BOOLEAN
        )
        """
        create_settings_table = """
        CREATE TABLE IF NOT EXISTS settings (
            ID INT PRIMARY KEY AUTO_INCREMENT,
            sound VARCHAR(255)
        )
        """
        create_reminders_table = """
        CREATE TABLE IF NOT EXISTS reminders (
            ID INT PRIMARY KEY AUTO_INCREMENT,
            reminder VARCHAR(255),
            datet DATETIME
        )
        """
        self.cursor.execute(create_pomodoro_table)
        self.cursor.execute(create_settings_table)
        self.cursor.execute(create_reminders_table)
        self.connection.commit()

    # CREATE functions
    def create_pomodoro_entry(self):
        insert_query = """
        INSERT INTO pomodoro_data (LogOn, Active)
        VALUES (%s, %s)
        """
        self.cursor.execute(insert_query, (datetime.now(), True))
        self.connection.commit()
        return self.cursor.lastrowid

    def create_reminder(self, reminder_text, reminder_date):
        insert_query = """
        INSERT INTO reminders (reminder, datet)
        VALUES (%s, %s)
        """
        self.cursor.execute(insert_query, (reminder_text, reminder_date))
        self.connection.commit()
        return self.cursor.lastrowid

    # READ functions
    def get_pomodoro_entry(self, entry_id):
        select_query = "SELECT * FROM pomodoro_data WHERE ID = %s"
        self.cursor.execute(select_query, (entry_id,))
        return self.cursor.fetchone()

    def get_all_pomodoro_entries(self):
        select_query = "SELECT * FROM pomodoro_data"
        self.cursor.execute(select_query)
        return self.cursor.fetchall()

    def get_reminder(self, reminder_id):
        select_query = "SELECT * FROM reminders WHERE ID = %s"
        self.cursor.execute(select_query, (reminder_id,))
        return self.cursor.fetchone()

    def get_all_reminders(self):
        select_query = "SELECT * FROM reminders"
        self.cursor.execute(select_query)
        return self.cursor.fetchall()
    
    def get_setting(self):
        select_query = "SELECT sound FROM settings"
        self.cursor.execute(select_query)
        return self.cursor.fetchone()

    # UPDATE functions
    def update_pomodoro_entry(self, entry_id, log_off=None, promo_time=None, active=None):
        update_query = "UPDATE pomodoro_data SET "
        update_params = []
        if log_off:
            update_query += "LogOff = %s, "
            update_params.append(log_off)
        if promo_time is not None:
            update_query += "PromoTime = %s, "
            update_params.append(promo_time)
        if active is not None:
            update_query += "Active = %s, "
            update_params.append(active)
        update_query = update_query.rstrip(', ') + " WHERE ID = %s"
        update_params.append(entry_id)
        
        self.cursor.execute(update_query, tuple(update_params))
        self.connection.commit()

    def update_reminder(self, reminder_id, reminder_text=None, reminder_date=None):
        update_query = "UPDATE reminders SET "
        update_params = []
        if reminder_text:
            update_query += "reminder = %s, "
            update_params.append(reminder_text)
        if reminder_date:
            update_query += "datet = %s, "
            update_params.append(reminder_date)
        update_query = update_query.rstrip(', ') + " WHERE ID = %s"
        update_params.append(reminder_id)
        
        self.cursor.execute(update_query, tuple(update_params))
        self.connection.commit()

    def get_todos(self):
        self.cursor.execute("SELECT todo FROM todos")
        return [todo[0] for todo in self.cursor.fetchall()]

    def save_todos(self, todos):
        self.cursor.execute("DELETE FROM todos")
        for todo in todos:
            self.cursor.execute("INSERT INTO todos (todo) VALUES (%s)", (todo,))
        self.connection.commit()



    # DELETE functions
    def delete_pomodoro_entry(self, entry_id):
        delete_query = "DELETE FROM pomodoro_data WHERE ID = %s"
        self.cursor.execute(delete_query, (entry_id,))
        self.connection.commit()

    def delete_reminder(self, reminder_id):
        delete_query = "DELETE FROM reminders WHERE ID = %s"
        self.cursor.execute(delete_query, (reminder_id,))
        self.connection.commit()

    def close(self, time, sound):
        update_query = """
        UPDATE pomodoro_data
        SET LogOff = %s, PromoTime = %s, Active = True
        WHERE ID = (SELECT MAX(ID) FROM (SELECT ID FROM pomodoro_data) AS temp)
        """
        # Convert time string back to seconds
        time_parts = time.split(':')
        time_seconds = int(time_parts[0]) * 60 + int(time_parts[1])
        
        self.cursor.execute(update_query, (datetime.now(), time_seconds))

        # Update or insert sound setting
        insert_sound_query = """
        INSERT INTO settings (sound) VALUES (%s)
        ON DUPLICATE KEY UPDATE sound = %s
        """
        self.cursor.execute(insert_sound_query, (sound, sound))

        self.connection.commit()
        self.connection.close()

    def main(self):
        self.connect()


if __name__ == '__main__':
    data = DataControl()
    data.main()