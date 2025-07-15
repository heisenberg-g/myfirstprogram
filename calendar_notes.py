#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重构版日历笔记程序（增删改完善）
---------------------------------
**新特性**
1. **删除笔记**
   - 每个笔记页签右上角新增 🗑 按钮，点击即可删除当前页签。
   - 删除后立即保存；若当天已无笔记，则自动创建一个空白页，避免只剩“＋”页。
2. 其他功能（回溯、无限新建、标签同步）保持一致。
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
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
        self.geometry('760x600')

        # 数据
        self.notes: dict[str, list[dict]] = {}
        self.selected_date = datetime.now().date()
        self.load_notes()

        # UI
        self.create_widgets()
        self.display_notes_for_date(self.selected_date.strftime('%Y-%m-%d'))

    # ---------------- 数据读写 ---------------- #
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

    # ---------------- UI 创建 ---------------- #
    def create_widgets(self):
        # 顶部栏：日期显示 + 切换按钮
        top_bar = ttk.Frame(self)
        top_bar.pack(fill='x', pady=5)

        self.date_label = ttk.Label(top_bar, text=self.selected_date.strftime('%Y-%m-%d'), cursor='hand2', font=('微软雅黑', 12, 'bold'))
        self.date_label.pack(side='left', padx=10)
        self.date_label.bind('<Button-1>', lambda _e: self.toggle_calendar())

        self.calendar_button = ttk.Button(top_bar, text='📅', width=3, command=self.toggle_calendar)
        self.calendar_button.pack(side='left')

        # 日历弹窗
        self.calendar_frame = tk.Frame(self)
        self.calendar = Calendar(self.calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack()
        self.calendar.bind('<<CalendarSelected>>', self.on_date_selected)
        self.calendar_visible = False
        self.update_calendar_marks()

        # 笔记区域
        self.notes_frame = tk.Frame(self)
        self.notes_frame.pack(fill='both', expand=True)

    # ---------------- 日历逻辑 ---------------- #
    def toggle_calendar(self):
        if self.calendar_visible:
            self.calendar_frame.pack_forget()
        else:
            self.calendar_frame.pack(pady=5)
        self.calendar_visible = not self.calendar_visible

    def on_date_selected(self, _event=None):
        date_str = self.calendar.get_date()
        self.selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        self.date_label.config(text=date_str)
        self.display_notes_for_date(date_str)
        # 保持日历开启，方便连续查看

    def update_calendar_marks(self):
        """为有笔记的日期打浅蓝背景"""
        self.calendar.calevent_remove('all')
        for date_str, entries in self.notes.items():
            if entries:
                try:
                    self.calendar.calevent_create(datetime.strptime(date_str, '%Y-%m-%d'), 'note', 'has_note')
                except ValueError:
                    continue
        self.calendar.tag_config('has_note', background='lightblue')

    # ---------------- 笔记逻辑 ---------------- #
    def display_notes_for_date(self, date_str: str):
        # 清空旧控件
        for widget in self.notes_frame.winfo_children():
            widget.destroy()

        # Notebook
        self.notebook = ttk.Notebook(self.notes_frame)
        self.notebook.pack(fill='both', expand=True)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

        self.entry_widgets: list[tuple[tk.StringVar, tk.Text]] = []

        # 载入已有笔记
        for note in self.notes.get(date_str, []):
            self._create_note_tab(note.get('tag', TAGS[0]), note.get('content', ''))

        # 若当天无笔记，创建空白页
        if not self.entry_widgets:
            self._create_note_tab()

        # "＋" 页
        self.plus_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plus_tab, text='＋')

    def _create_note_tab(self, tag: str = '', content: str = ''):
        """插入一个新的笔记页签（位于“＋”前）"""
        frame = ttk.Frame(self.notebook)
        insert_idx = self.notebook.index(self.plus_tab) if hasattr(self, 'plus_tab') and str(self.plus_tab) in self.notebook.tabs() else 'end'
        self.notebook.insert(insert_idx, frame, text=tag or '新笔记')

        # 头部行：标签选择 + 删除按钮
        header = ttk.Frame(frame)
        header.pack(fill='x', pady=5, padx=5)

        tag_var = tk.StringVar(value=tag or TAGS[0])
        tag_cb = ttk.Combobox(header, textvariable=tag_var, values=TAGS + ['+ 新标签'], width=12)
        tag_cb.pack(side='left')
        tag_cb.bind('<<ComboboxSelected>>', lambda _e, v=tag_var, cb=tag_cb: self.handle_tag_change(v, cb))

        del_btn = ttk.Button(header, text='🗑 删除', command=lambda f=frame: self.delete_note_tab(f))
        del_btn.pack(side='right')

        # 文本框
        text_widget = tk.Text(frame, wrap='word')
        text_widget.insert('1.0', content)
        text_widget.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        text_widget.bind('<FocusOut>', lambda _e: self.auto_save())

        self.entry_widgets.append((tag_var, text_widget))

    # ----------- 事件处理 ----------- #
    def on_tab_changed(self, _event=None):
        if self.notebook.select() == str(self.plus_tab):
            self._create_note_tab()
            self.notebook.select(self.notebook.index(self.plus_tab) - 1)

    def handle_tag_change(self, tag_var: tk.StringVar, combobox: ttk.Combobox):
        if tag_var.get() == '+ 新标签':
            new_tag = simpledialog.askstring('新标签', '请输入新标签名称：')
            tag_var.set(new_tag or TAGS[0])
            if new_tag:
                TAGS.append(new_tag)
                combobox['values'] = TAGS + ['+ 新标签']
        # 更新页签标题
        frame = combobox.master.master  # header 的父 frame
        self.notebook.tab(frame, text=tag_var.get())
        self.auto_save()

    def delete_note_tab(self, frame: ttk.Frame):
        if frame == self.plus_tab:
            return  # 安全检查
        # 移除 entry_widgets 记录
        self.entry_widgets = [(v, t) for (v, t) in self.entry_widgets if t.master != frame]
        self.notebook.forget(frame)
        frame.destroy()
        self.auto_save()
        # 若删完仅剩"＋"页，则留一个空白
        if len(self.entry_widgets) == 0:
            self._create_note_tab()
            self.notebook.select(self.notebook.index(self.plus_tab) - 1)

    # ----------- 保存 ----------- #
    def auto_save(self):
        date_str = self.selected_date.strftime('%Y-%m-%d')
        day_data = []
        for tag_var, text_widget in self.entry_widgets:
            content = text_widget.get('1.0', tk.END).strip()
            if content:
                day_data.append({'tag': tag_var.get(), 'content': content})
        if day_data:
            self.notes[date_str] = day_data
        elif date_str in self.notes:
            del self.notes[date_str]
        self.save_notes()
        self.update_calendar_marks()


if __name__ == '__main__':
    app = CalendarNoteApp()
    app.mainloop()
