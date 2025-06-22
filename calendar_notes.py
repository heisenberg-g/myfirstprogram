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
        self.update_calendar_events()
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
        self.update_calendar_events()

    def update_calendar_events(self):
        if not hasattr(self, 'calendar'):
            return
        self.calendar.calevent_remove('all')
        self.calendar.tag_config('note', background='orange', foreground='white')
        for date_str, notes in self.notes.items():
            if notes:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    continue
                self.calendar.calevent_create(date_obj, str(len(notes)), 'note')

    def create_widgets(self):
        # 顶部小按钮显示日历
        self.calendar_button = ttk.Button(self, text='选择日期', command=self.toggle_calendar)
        self.calendar_button.pack(pady=5)

        # 当前日期简易显示
        self.date_label = ttk.Label(self, text=self.selected_date.strftime('%m/%d/%Y'))
        self.date_label.pack()

        # 日历（默认隐藏）
        self.calendar_frame = tk.Frame(self)
        self.calendar = Calendar(self.calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack()
        self.calendar.bind('<<CalendarSelected>>', self.on_date_selected)
        self.calendar_visible = False

        # 笔记输入区域
        self.notes_frame = tk.Frame(self)
        self.notes_frame.pack(fill='both', expand=True)
        # 笔记以标签页形式展示
        self.notebook = ttk.Notebook(self.notes_frame)
        self.notebook.pack(fill='both', expand=True)

        self.add_note_btn = ttk.Button(self.notes_frame, text='新建笔记', command=lambda: self.add_note_tab())
        self.add_note_btn.pack(pady=5)

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
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        self.entry_widgets = []

        date_notes = self.notes.get(date_str, [])
        if date_notes:
            for note in date_notes:
                self.add_note_tab(note.get('tag', TAGS[0]), note.get('content', ''))
        else:
            self.add_note_tab()

        # 更新日期显示
        self.date_label.config(text=self.selected_date.strftime('%m/%d/%Y'))

    def add_note_tab(self, tag='', content=''):
        frame = tk.Frame(self.notebook, pady=5)

        tag_var = tk.StringVar(value=tag if tag else TAGS[0])
        tag_dropdown = ttk.Combobox(frame, textvariable=tag_var, values=TAGS, width=10)
        tag_dropdown.pack(side='top', anchor='w', padx=5, pady=2)

        text = tk.Text(frame, height=10)
        text.insert('1.0', content)
        text.pack(fill='both', expand=True, padx=5, pady=5)
        text.bind('<FocusOut>', lambda e: self.auto_save())

        self.entry_widgets.append((tag_var, text))
        index = len(self.entry_widgets)
        self.notebook.add(frame, text=f'笔记{index}')
        self.notebook.select(frame)

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
