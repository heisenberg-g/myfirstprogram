import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar

NOTES_FILE = 'notes.json'

class CalendarNoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Calendar Notes')
        self.geometry('400x400')
        self.resizable(False, False)

        self.notes = {}
        self.selected_date = datetime.now().date()
        self.load_notes()
        self.create_widgets()

    def load_notes(self):
        if os.path.exists(NOTES_FILE):
            try:
                with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                    self.notes = json.load(f)
            except Exception as e:
                messagebox.showerror('Error', f'Failed to load notes: {e}')
        else:
            self.notes = {}

    def save_notes(self):
        try:
            with open(NOTES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save notes: {e}')

    def create_widgets(self):
        self.calendar = Calendar(self, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack(pady=10)
        self.calendar.bind('<<CalendarSelected>>', self.on_date_selected)

        self.text = tk.Text(self, width=40, height=10)
        self.text.pack(pady=10)

        btn = ttk.Button(self, text='Save Note', command=self.on_save)
        btn.pack(pady=5)

        # Load note for today's date initially
        self.display_note_for_date(self.selected_date.strftime('%Y-%m-%d'))

    def on_date_selected(self, event):
        date_str = self.calendar.get_date()
        self.selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        self.display_note_for_date(date_str)

    def display_note_for_date(self, date_str):
        note = self.notes.get(date_str, '')
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, note)

    def on_save(self):
        content = self.text.get('1.0', tk.END).rstrip()
        date_str = self.selected_date.strftime('%Y-%m-%d')
        if content:
            self.notes[date_str] = content
        elif date_str in self.notes:
            del self.notes[date_str]
        self.save_notes()
        messagebox.showinfo('Saved', f'Note for {date_str} saved')

if __name__ == '__main__':
    app = CalendarNoteApp()
    app.mainloop()
