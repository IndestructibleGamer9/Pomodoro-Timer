import matplotlib as plt
import pandas as pd 
import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl import Workbook

USERNAME = 'TESTING'

class DataControl():
    def __init__(self):
        pass

    def connect(self, username='AnonymousUser'):
        filename = f'{username}.xlsx'
        try:
            self.wb = openpyxl.load_workbook(filename)
        except FileNotFoundError:
            print('File not found. Creating new file.')
            self.create_workbook(username)
        except InvalidFileException:
            print('Invalid file format. Creating new file.')
            self.create_workbook(username)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")    

    def create_workbook(self, name):
        self.wb = Workbook()
        fn = f'{name}.xlsx'

        # Format WB
        self.ws1 = self.wb.active  # Note: this is a property, not a method
        self.ws1.title = "Pomodoro Timer Data"
        self.ws2 = self.wb.create_sheet(title='Settings')
        self.ws3 = self.wb.create_sheet(title='Reminders')

        self.wb.save(fn)

    def main(self):
        self.connect(USERNAME)

if __name__ == '__main__':
    data = DataControl()
    data.main()