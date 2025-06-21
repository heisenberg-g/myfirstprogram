# Codex Task: 重构日历笔记界面
# 优化点：
# 1. 缩小日历到顶部图标（点击弹出）
# 2. 支持多个笔记输入框，每个都有分类标签（金融/日记/专业课）
# 3. 文本框自动保存，无需点击按钮
# 4. 可扩展标签种类

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import json
import os
from datetime import datetime

NOTES_FILE = 'notes.json'
TAGS = ['金融', '日记', '专业课']

class CalendarNoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('日历笔记')
        self.geometry('600x500')

        self.notes = {}
        self.selected_date = datetime.now().date()
        self.load_notes()

        self.create_widgets()
        self.display_notes_for_date(self.selected_date.strftime('%Y-%m-%d'))

    def load_notes(self):
        if os.path.exists(NOTES_FILE):
            try:
                with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                    self.notes = json.load(f)
            except Exception as e:
                messagebox.showerror('加载失败', f'{e}')
        else:
            self.notes = {}

    def save_notes(self):
        try:
            with open(NOTES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror('保存失败', f'{e}')

    def create_widgets(self):
        # 顶部小按钮显示日历
        self.calendar_button = ttk.Button(self, text='选择日期', command=self.toggle_calendar)
        self.calendar_button.pack(pady=5)

        # 日历（默认隐藏）
        self.calendar_frame = tk.Frame(self)
        self.calendar = Calendar(self.calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack()
        self.calendar.bind('<<CalendarSelected>>', self.on_date_selected)
        self.calendar_visible = False

        # 笔记输入区域
        self.notes_frame = tk.Frame(self)
        self.notes_frame.pack(fill='both', expand=True)

    def toggle_calendar(self):
        if self.calendar_visible:
            self.calendar_frame.pack_forget()
            self.calendar_visible = False
        else:
            self.calendar_frame.pack(pady=5)
            self.calendar_visible = True

    def on_date_selected(self, event):
        date_str = self.calendar.get_date()
        self.selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        self.display_notes_for_date(date_str)
        self.toggle_calendar()  # 自动关闭日历

    def display_notes_for_date(self, date_str):
        for widget in self.notes_frame.winfo_children():
            widget.destroy()

        self.entry_widgets = []

        date_notes = self.notes.get(date_str, [])
        for note in date_notes:
            self.add_note_entry(note.get('tag', TAGS[0]), note.get('content', ''))

        # 默认添加一个空笔记（可选）
        self.add_note_entry()

    def add_note_entry(self, tag='', content=''):
        frame = tk.Frame(self.notes_frame, pady=5)
        frame.pack(fill='x', padx=10)

        tag_var = tk.StringVar(value=tag if tag else TAGS[0])
        tag_dropdown = ttk.Combobox(frame, textvariable=tag_var, values=TAGS, width=10)
        tag_dropdown.pack(side='left')

        text = tk.Text(frame, height=3, width=60)
        text.insert('1.0', content)
        text.pack(side='left', padx=5)
        text.bind('<FocusOut>', lambda e: self.auto_save())

        self.entry_widgets.append((tag_var, text))

    def auto_save(self):
        date_str = self.selected_date.strftime('%Y-%m-%d')
        entry_data = []
        for tag_var, text_widget in self.entry_widgets:
            content = text_widget.get('1.0', tk.END).strip()
            if content:
                entry_data.append({'tag': tag_var.get(), 'content': content})
        self.notes[date_str] = entry_data
        self.save_notes()

if __name__ == '__main__':
    app = CalendarNoteApp()
    app.mainloop()
