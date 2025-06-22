# Calendar Notes App

这是一个基于 Python 和 Tkinter 的本地日历笔记软件，所有笔记都会保存在当前目录下的 `notes.json` 文件中。

## 依赖

- Python 3.11+
- Tkinter（Python 自带）
- [tkcalendar](https://pypi.org/project/tkcalendar/) 库

使用 pip 安装依赖：

```bash
pip install tkcalendar
```

## 运行

```bash
python3 calendar_notes.py
```

程序启动后会在顶部显示当前日期，点击 **选择日期** 按钮可弹出日历。日历中每个有笔记的日期下方都会显示带颜色的数字提示。选择日期后在下方的标签页中编辑笔记即可，内容会自动保存，无需额外的保存按钮。
