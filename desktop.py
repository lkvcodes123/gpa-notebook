"""Native GPA calculator. Run: python3 desktop.py"""
import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from app import GRADES, LEVELS, calculate

SAVE_FILE = Path.home() / 'Library' / 'Application Support' / 'GPA Notebook' / 'courses.json'


class GpaApp:
    def __init__(self, window):
        self.window = window
        window.title('GPA Notebook')
        window.geometry('940x640')
        window.minsize(720, 480)
        self.semesters = []
        self.loading = True
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Helvetica', 28, 'bold'))
        style.configure('Result.TLabel', font=('Helvetica', 24, 'bold'), foreground='#65499a')
        style.configure('Muted.TLabel', foreground='#797080')

        body = ttk.Frame(window, padding=24)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text='GPA Notebook', style='Title.TLabel').pack(anchor='w')
        ttk.Label(body, text='Your courses. Your progress.', style='Muted.TLabel').pack(anchor='w', pady=(5, 20))

        summary = ttk.Frame(body)
        summary.pack(fill='x')
        self.totals = []
        for title in ('Overall GPA', 'Unweighted GPA', 'Graded credits'):
            frame = ttk.LabelFrame(summary, text=title, padding=14)
            frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
            value = ttk.Label(frame, text='—', style='Result.TLabel')
            value.pack(anchor='w')
            self.totals.append(value)

        toolbar = ttk.Frame(body)
        toolbar.pack(fill='x', pady=16)
        ttk.Button(toolbar, text='+ Add semester', command=self.add_semester).pack(side='left')
        ttk.Button(toolbar, text='Grading guide', command=self.show_guide).pack(side='right')
        ttk.Button(toolbar, text='Reset all', command=self.reset).pack(side='right', padx=8)
        self.tabs = ttk.Notebook(body)
        self.tabs.pack(fill='both', expand=True)
        self.status = ttk.Label(body, text='', style='Muted.TLabel')
        self.status.pack(anchor='w', pady=(12, 0))

        saved = self.load()
        for semester in saved:
            self.add_semester(semester)
        self.loading = False
        self.update()

    def load(self):
        try:
            saved = json.loads(SAVE_FILE.read_text())
            calculate(saved)
            return saved['semesters']
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            return [{'weighted': True, 'courses': [{} for _ in range(3)]}]

    def add_semester(self, saved=None):
        saved = saved or {'weighted': True, 'courses': [{} for _ in range(3)]}
        page = ttk.Frame(self.tabs, padding=16)
        semester = {'page': page, 'weighted': tk.BooleanVar(value=saved['weighted']), 'rows': []}
        self.semesters.append(semester)
        self.tabs.add(page, text=f'Semester {len(self.semesters)}')
        self.tabs.select(page)

        top = ttk.Frame(page)
        top.pack(fill='x', pady=(0, 12))
        ttk.Checkbutton(top, text='Weighted GPA', variable=semester['weighted'], command=self.update).pack(side='left')
        ttk.Button(top, text='Remove semester', command=lambda: self.remove_semester(semester)).pack(side='right')
        semester['result'] = ttk.Label(top, text='Semester GPA: —')
        semester['result'].pack(side='right', padx=16)

        # A scrollable area keeps long course lists usable.
        area = ttk.Frame(page)
        area.pack(fill='both', expand=True)
        canvas = tk.Canvas(area, highlightthickness=0)
        scrollbar = ttk.Scrollbar(area, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        rows = ttk.Frame(canvas)
        item = canvas.create_window((0, 0), window=rows, anchor='nw')
        rows.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda event: canvas.itemconfigure(item, width=event.width))
        semester['container'] = rows
        for column, title in enumerate(('Course name', 'Grade', 'Credits', 'Course level', '')):
            ttk.Label(rows, text=title).grid(row=0, column=column, sticky='w', padx=5, pady=6)
        rows.columnconfigure(0, weight=1)
        for course in saved['courses']:
            self.add_course(semester, course)
        ttk.Button(page, text='+ Add course', command=lambda: self.add_course(semester)).pack(anchor='w', pady=(12, 0))
        self.update()

    def add_course(self, semester, saved=None):
        saved = saved or {}
        row = {'values': {}, 'widgets': []}
        defaults = {'name': '', 'grade': '', 'credits': '5', 'level': 'Regular'}
        grid_row = max([widget.grid_info()['row'] for widget in semester['container'].winfo_children()] + [0]) + 1
        for column, (field, default) in enumerate(defaults.items()):
            variable = tk.StringVar(value=str(saved.get(field, default)))
            row['values'][field] = variable
            if field in ('grade', 'level'):
                choices = ['', *GRADES] if field == 'grade' else list(LEVELS)
                widget = ttk.Combobox(semester['container'], textvariable=variable, values=choices,
                                      state='readonly', width=9 if field == 'grade' else 14)
            else:
                widget = ttk.Entry(semester['container'], textvariable=variable, width=24 if field == 'name' else 8)
            widget.grid(row=grid_row, column=column, sticky='ew', padx=5, pady=5)
            row['widgets'].append(widget)
            variable.trace_add('write', lambda *_: self.update())
        button = ttk.Button(semester['container'], text='Remove', command=lambda: self.remove_course(semester, row))
        button.grid(row=grid_row, column=4, padx=5)
        row['widgets'].append(button)
        semester['rows'].append(row)
        self.update()

    def remove_course(self, semester, row):
        for widget in row['widgets']:
            widget.destroy()
        semester['rows'].remove(row)
        self.update()

    def remove_semester(self, semester):
        if not messagebox.askyesno('Remove semester', 'Remove this semester and its courses?'):
            return
        self.tabs.forget(semester['page'])
        semester['page'].destroy()
        self.semesters.remove(semester)
        for number, item in enumerate(self.semesters, 1):
            self.tabs.tab(item['page'], text=f'Semester {number}')
        self.update()

    def update(self):
        if self.loading:
            return
        data = {'semesters': [
            {'weighted': semester['weighted'].get(),
             'courses': [{key: value.get() for key, value in row['values'].items()} for row in semester['rows']]}
            for semester in self.semesters
        ]}
        try:
            result = calculate(data)
            for label, key in zip(self.totals, ('gpa', 'unweighted', 'credits')):
                value = result[key]
                label.configure(text='—' if value is None else f'{value:.2f}' if key != 'credits' else f'{value:g}')
            for semester, values in zip(self.semesters, result['semesters']):
                value = values['gpa']
                semester['result'].configure(text='Semester GPA: ' + ('—' if value is None else f'{value:.2f}'))
            self.status.configure(text='Saved automatically on this Mac')
        except ValueError as error:
            for label in self.totals:
                label.configure(text='—')
            for semester in self.semesters:
                semester['result'].configure(text='Semester GPA: —')
            self.status.configure(text=str(error))
        try:
            SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
            temporary = SAVE_FILE.with_suffix('.tmp')
            temporary.write_text(json.dumps(data))
            temporary.replace(SAVE_FILE)
        except OSError:
            self.status.configure(text='Could not save coursework on this Mac.')

    def reset(self):
        if not messagebox.askyesno('Reset calculator', 'Clear all coursework?'):
            return
        self.loading = True
        for semester in self.semesters:
            semester['page'].destroy()
        self.semesters.clear()
        self.add_semester()
        self.loading = False
        self.update()

    def show_guide(self):
        messagebox.showinfo('Grading guide',
            'GPA = total quality points ÷ graded credits.\n\n'
            'Regular: +0.0   •   Honors: +0.5   •   AP / IB: +1.0\n'
            'Bonuses apply when Weighted GPA is checked.\n'
            'F earns 0; P, W, I and blank grades are excluded.\n\n'
            + '\n'.join(f'{grade}: {points}' for grade, points in GRADES.items() if points is not None)
            + '\n\nOverall GPA uses each semester’s weighting setting.\nSchool policies may differ.')


if __name__ == '__main__':
    root = tk.Tk()
    GpaApp(root)
    root.mainloop()
