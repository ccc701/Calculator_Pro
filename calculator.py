import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from math import sqrt
import json
import os
import re

class ModernCalculator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("计算器 Pro")
        self.window.resizable(False, False)
        self.window.configure(bg='#2b2b2b')
        
        self.memory = 0
        self.full_expression = ""
        self.current_file = None
        self.history = []
        self.percent_base = None
        self.setup_styles()
        self.setup_menu()
        self.setup_display()
        self.reset_state()
        self.setup_buttons()
        self.bind_keys()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Save.TButton',
                       background='#4CAF50',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'))
        style.map('Save.TButton',
                 background=[('active', '#45a049')])
        
        style.configure('Open.TButton',
                       background='#2196F3',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'))
        style.map('Open.TButton',
                 background=[('active', '#1976D2')])
    
    def setup_menu(self):
        menu_frame = tk.Frame(self.window, bg='#2b2b2b', height=40)
        menu_frame.grid(row=0, column=0, columnspan=6, sticky="ew", padx=5, pady=5)
        
        self.save_btn = tk.Button(
            menu_frame,
            text="💾 保存算式",
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.save_calculation
        )
        self.save_btn.pack(side='left', padx=2)
        
        self.open_btn = tk.Button(
            menu_frame,
            text="📂 打开算式",
            bg='#2196F3',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.open_calculation
        )
        self.open_btn.pack(side='left', padx=2)
        
        self.bin_var = tk.BooleanVar()
        self.bin_check = tk.Checkbutton(
            menu_frame,
            text="二进制模式",
            variable=self.bin_var,
            command=self.toggle_binary_mode,
            bg='#2b2b2b',
            fg='white',
            selectcolor='#2b2b2b',
            font=('Arial', 10),
            activebackground='#2b2b2b',
            activeforeground='white',
            cursor='hand2'
        )
        self.bin_check.pack(side='right', padx=10)
        
        self.mode_label = tk.Label(
            menu_frame,
            text="DEC",
            bg='#2b2b2b',
            fg='#ff9800',
            font=('Arial', 10, 'bold')
        )
        self.mode_label.pack(side='right', padx=5)
    
    def reset_state(self):
        self.current_input = "0"
        self.previous_input = ""
        self.current_operator = ""
        self.result_displayed = False
        self.display_var.set("0")
        self.expression_var.set("")
        self.full_expression = ""
        self.binary_mode = False
        self.percent_base = None
    
    def setup_display(self):
        self.expression_var = tk.StringVar(value="")
        self.display_var = tk.StringVar(value="0")
        
        display_frame = tk.Frame(self.window, bg='#1e1e1e', bd=2, relief=tk.FLAT)
        display_frame.grid(row=1, column=0, columnspan=6, sticky="nsew", padx=10, pady=5)
        
        self.expression_label = tk.Label(
            display_frame,
            textvariable=self.expression_var,
            font=("Consolas", 12),
            anchor="e",
            fg="#888888",
            bg='#1e1e1e',
            height=1
        )
        self.expression_label.pack(fill='x', padx=10, pady=(10,0))
        
        self.display = tk.Entry(
            display_frame,
            textvariable=self.display_var,
            font=("Consolas", 24, "bold"),
            justify="right",
            bd=0,
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief=tk.FLAT
        )
        self.display.pack(fill='both', expand=True, padx=10, pady=(0,10))
    
    def create_button(self, text, row, col, colspan=1, color='#3c3c3c', text_color='#ffffff', 
                      hover_color='#4a4a4a', special=False):
        btn = tk.Button(
            self.window,
            text=text,
            font=("Arial", 12, "bold"),
            bd=0,
            bg=color,
            fg=text_color,
            activebackground=hover_color,
            activeforeground=text_color,
            cursor='hand2',
            command=lambda t=text: self.button_click(t)
        )
        
        if colspan > 1:
            btn.grid(row=row, column=col, columnspan=colspan, padx=1, pady=1, sticky="nsew")
        else:
            btn.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
        
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover_color))
        btn.bind("<Leave>", lambda e: btn.configure(bg=color))
        
        return btn
    
    def setup_buttons(self):
        button_configs = [
            ('MC', 3, 0, 1, '#2d2d2d', '#ff6b6b', '#3a3a3a'),
            ('MR', 3, 1, 1, '#2d2d2d', '#4ecdc4', '#3a3a3a'),
            ('M+', 3, 2, 1, '#2d2d2d', '#ffe66d', '#3a3a3a'),
            ('M-', 3, 3, 1, '#2d2d2d', '#ff9f43', '#3a3a3a'),
            ('MS', 3, 4, 1, '#2d2d2d', '#a29bfe', '#3a3a3a'),
            ('MU', 3, 5, 1, '#2d2d2d', '#fd79a8', '#3a3a3a'),
            
            ('C', 4, 0, 1, '#e74c3c', '#ffffff', '#c0392b'),
            ('±', 4, 1, 1, '#34495e', '#ffffff', '#2c3e50'),
            ('mod', 4, 2, 1, '#34495e', '#ffffff', '#2c3e50'),
            ('÷', 4, 3, 1, '#f39c12', '#ffffff', '#e67e22'),
            ('√', 4, 4, 1, '#34495e', '#ffffff', '#2c3e50'),
            ('(', 4, 5, 1, '#34495e', '#ffffff', '#2c3e50'),
            
            ('7', 5, 0, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            ('8', 5, 1, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            ('9', 5, 2, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            ('×', 5, 3, 1, '#f39c12', '#ffffff', '#e67e22'),
            ('x²', 5, 4, 1, '#34495e', '#ffffff', '#2c3e50'),
            (')', 5, 5, 1, '#34495e', '#ffffff', '#2c3e50'),
            
            ('4', 6, 0, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            ('5', 6, 1, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            ('6', 6, 2, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            ('-', 6, 3, 1, '#f39c12', '#ffffff', '#e67e22'),
            ('//', 6, 4, 1, '#34495e', '#ffffff', '#2c3e50'),
            ('.', 6, 5, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            
            ('1', 7, 0, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            ('2', 7, 1, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            ('3', 7, 2, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            ('+', 7, 3, 1, '#f39c12', '#ffffff', '#e67e22'),
            ('%', 7, 4, 1, '#34495e', '#ffffff', '#2c3e50'),
            ('+/-', 7, 5, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            
            ('0', 8, 0, 2, '#4a4a4a', '#ffffff', '#5a5a5a'),
            ('00', 8, 2, 1, '#4a4a4a', '#ffffff', '#5a5a5a'),
            ('⌫', 8, 3, 1, '#e67e22', '#ffffff', '#d35400'),
            ('=', 8, 4, 2, '#3498db', '#ffffff', '#2980b9'),
        ]
        
        self.buttons = {}
        for config in button_configs:
            text, row, col, colspan, color, text_color, hover_color = config
            self.buttons[text] = self.create_button(text, row+1, col, colspan, color, text_color, hover_color)
        
        for i in range(6):
            self.window.grid_columnconfigure(i, weight=1, minsize=80)
        for i in range(9):
            self.window.grid_rowconfigure(i, weight=1, minsize=50)
    
    def bind_keys(self):
        self.window.bind('<Key>', self.key_press)
        self.window.bind('<Return>', lambda e: self.button_click('='))
        self.window.bind('<BackSpace>', lambda e: self.button_click('⌫'))
        self.window.bind('<Escape>', lambda e: self.button_click('C'))
        self.window.bind('<parenleft>', lambda e: self.button_click('('))
        self.window.bind('<parenright>', lambda e: self.button_click(')'))
        self.window.bind('<Control-s>', lambda e: self.save_calculation())
        self.window.bind('<Control-o>', lambda e: self.open_calculation())
        self.window.focus_set()
    
    def key_press(self, event):
        key = event.char
        key_map = {
            '*': '×',
            '/': '÷',
            '%': '%',
            '+': '+',
            '-': '-',
            '.': '.',
            '=': '='
        }
        
        if key in '0123456789':
            if self.binary_mode and key not in '01':
                messagebox.showwarning("二进制模式", "二进制模式下只能输入0或1")
                return
            self.button_click(key)
        elif key in key_map:
            if self.binary_mode and key == '%':
                messagebox.showwarning("二进制模式", "二进制模式下不能使用百分比")
                return
            self.button_click(key_map[key])
    
    def toggle_binary_mode(self):
        self.binary_mode = self.bin_var.get()
        if self.binary_mode:
            self.mode_label.config(text="BIN", fg='#4CAF50')
            if self.current_input:
                try:
                    dec_val = int(float(self.current_input))
                    self.current_input = bin(dec_val)[2:]
                    self.display_var.set(self.current_input)
                except:
                    self.display_var.set("0")
                    self.current_input = "0"
        else:
            self.mode_label.config(text="DEC", fg='#ff9800')
            if self.current_input:
                try:
                    bin_val = int(self.current_input, 2)
                    self.current_input = str(bin_val)
                    self.display_var.set(self.current_input)
                except:
                    self.display_var.set("0")
                    self.current_input = "0"
    
    def convert_to_binary(self, value):
        try:
            if value < 0:
                return "-" + bin(abs(int(value)))[2:]
            if '.' in str(value):
                int_part = int(float(value))
                dec_part = float(value) - int_part
                bin_int = bin(int_part)[2:]
                bin_dec = ""
                for _ in range(8):
                    dec_part *= 2
                    if dec_part >= 1:
                        bin_dec += "1"
                        dec_part -= 1
                    else:
                        bin_dec += "0"
                return f"{bin_int}.{bin_dec}"
            else:
                return bin(int(value))[2:]
        except:
            return "0"
    
    def save_calculation(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".cnt",
            filetypes=[("计算器算式", "*.cnt"), ("所有文件", "*.*")],
            title="保存算式"
        )
        
        if file_path:
            try:
                expression_to_save = self.full_expression
                if self.current_input != "0":
                    expression_to_save += self.current_input
                
                if not expression_to_save:
                    expression_to_save = self.display_var.get()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(expression_to_save)
                
                self.current_file = file_path
                messagebox.showinfo("成功", f"算式已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def open_calculation(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("计算器算式", "*.cnt"), ("所有文件", "*.*")],
            title="打开算式"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    saved_expression = f.read().strip()
                
                if saved_expression:
                    self.full_expression = saved_expression
                    self.expression_var.set(saved_expression)
                    self.current_input = "0"
                    self.display_var.set("0")
                    self.result_displayed = False
                    self.current_file = file_path
                    messagebox.showinfo("成功", f"算式已加载")
                else:
                    messagebox.showwarning("警告", "文件为空")
                
            except Exception as e:
                messagebox.showerror("错误", f"打开失败: {str(e)}")
    
    def update_display_expression(self):
        if self.full_expression:
            self.expression_var.set(self.full_expression)
        else:
            self.expression_var.set("")
    
    def button_click(self, text):
        if text in '0123456789':
            self.input_number(text)
        elif text == '00':
            self.input_double_zero()
        elif text == '.':
            self.input_decimal()
        elif text in '+-×÷':
            self.input_operator(text)
        elif text == 'mod':
            self.input_operator('%')
        elif text == '%':
            if self.binary_mode:
                messagebox.showwarning("二进制模式", "二进制模式下不能使用百分比")
                return
            self.input_percent()
        elif text == '=':
            self.calculate_expression()
        elif text == 'C':
            self.reset_state()
        elif text == '±' or text == '+/-':
            self.toggle_sign()
        elif text == '⌫':
            self.backspace()
        elif text == '√':
            self.sqrt_operation()
        elif text == 'x²':
            self.square_operation()
        elif text == '//':
            self.input_operator('//')
        elif text == '(':
            self.input_parenthesis('(')
        elif text == ')':
            self.input_parenthesis(')')
        elif text == 'MC':
            self.memory = 0
        elif text == 'MR':
            self.current_input = str(self.memory)
            self.display_var.set(self.current_input)
            self.result_displayed = False
        elif text == 'M+':
            if self.current_input and self.current_input != "0":
                self.memory += float(self.current_input)
        elif text == 'M-':
            if self.current_input and self.current_input != "0":
                self.memory -= float(self.current_input)
        elif text == 'MS':
            if self.current_input and self.current_input != "0":
                self.memory = float(self.current_input)
        elif text == 'MU':
            self.mu_operation()
    
    def input_number(self, num):
        if self.result_displayed:
            self.current_input = "0"
            self.full_expression = ""
            self.result_displayed = False
        
        if self.binary_mode:
            if num not in '01':
                messagebox.showwarning("二进制模式", "只能输入0或1")
                return
        
        if self.current_input == "0" and num != '.':
            self.current_input = num
        elif self.current_input == "-0" and num != '.':
            self.current_input = "-" + num
        else:
            self.current_input += num
        
        self.display_var.set(self.current_input)
        self.update_display_expression()
    
    def input_double_zero(self):
        if self.result_displayed:
            self.current_input = "0"
            self.full_expression = ""
            self.result_displayed = False
        
        if self.binary_mode:
            messagebox.showwarning("二进制模式", "只能输入0或1")
            return
        
        if self.current_input and self.current_input != "0":
            self.current_input += "00"
            self.display_var.set(self.current_input)
    
    def input_decimal(self):
        if self.binary_mode:
            return
            
        if self.result_displayed:
            self.current_input = "0"
            self.full_expression = ""
            self.result_displayed = False
        
        if '.' not in self.current_input:
            self.current_input += '.'
            self.display_var.set(self.current_input)
    
    def input_parenthesis(self, paren):
        if paren == '(':
            if self.current_input != "0" and not self.result_displayed:
                if self.full_expression:
                    self.full_expression += self.current_input
                else:
                    self.full_expression = self.current_input
            self.full_expression += "("
            self.current_input = "0"
            self.display_var.set("0")
            self.update_display_expression()
            self.result_displayed = False
        elif paren == ')':
            if self.current_input != "0":
                self.full_expression += self.current_input
                self.current_input = "0"
            self.full_expression += ")"
            self.display_var.set("0")
            self.update_display_expression()
            self.result_displayed = False
    
    def input_operator(self, op):
        if self.current_input != "0" and not self.result_displayed:
            if self.full_expression:
                self.full_expression += self.current_input
            else:
                self.full_expression = self.current_input
            self.percent_base = float(self.current_input)
        
        op_display = {'+': '+', '-': '-', '×': '*', '÷': '/', '%': '%', '//': '//'}
        
        if self.full_expression:
            if self.full_expression[-1] in '+-*/%' and op == '-':
                self.full_expression += "-"
            elif self.full_expression[-1] not in '+-*/%':
                self.full_expression += op_display.get(op, op)
        elif op == '-':
            self.full_expression = "-"
        
        self.current_input = "0"
        self.display_var.set("0")
        self.update_display_expression()
        self.result_displayed = False
    
    def input_percent(self):
        if self.binary_mode:
            messagebox.showwarning("二进制模式", "二进制模式下不能使用百分比")
            return
            
        if self.current_input != "0" and self.percent_base is not None:
            try:
                current_val = float(self.current_input)
                percent_val = self.percent_base * (current_val / 100)
                
                if self.full_expression:
                    self.full_expression += self.current_input
                else:
                    self.full_expression = self.current_input
                
                self.full_expression += "%"
                self.current_input = str(percent_val)
                self.display_var.set(self.current_input)
                self.update_display_expression()
                
            except:
                self.display_var.set("错误")
        elif self.current_input != "0":
            try:
                val = float(self.current_input)
                percent_val = val / 100
                self.current_input = str(percent_val)
                self.display_var.set(self.current_input)
                self.full_expression = f"{val}%"
                self.update_display_expression()
            except:
                self.display_var.set("错误")
    
    def calculate_expression(self):
        if self.current_input != "0":
            self.full_expression += self.current_input
        
        if not self.full_expression:
            return
        
        try:
            expr = self.full_expression
            
            if self.binary_mode:
                expr = self.parse_binary_expression(expr)
            
            expr = expr.replace('×', '*').replace('÷', '/')
            
            result = eval(expr, {"__builtins__": None}, {})
            
            self.history.append({
                "expression": self.full_expression,
                "result": result
            })
            
            if self.binary_mode:
                result_bin = self.convert_to_binary(result)
                self.display_var.set(result_bin)
                self.current_input = result_bin
            else:
                if isinstance(result, float):
                    if result == int(result):
                        result = int(result)
                    else:
                        result = round(result, 10)
                self.display_var.set(str(result))
                self.current_input = str(result)
            
            self.full_expression = ""
            self.expression_var.set("")
            self.result_displayed = True
            self.percent_base = None
            
        except ZeroDivisionError:
            self.display_var.set("错误")
            self.reset_state()
        except Exception as e:
            self.display_var.set("错误")
            self.reset_state()
    
    def parse_binary_expression(self, expr):
        parts = re.split(r'([+\-*/%()])', expr)
        converted_parts = []
        for part in parts:
            if part and part not in '+-*/%()':
                if all(c in '01.' for c in part):
                    if '.' in part:
                        int_part, dec_part = part.split('.')
                        dec_val = int(int_part, 2)
                        for i, bit in enumerate(dec_part):
                            if bit == '1':
                                dec_val += 2 ** -(i+1)
                        converted_parts.append(str(dec_val))
                    else:
                        converted_parts.append(str(int(part, 2)))
                else:
                    converted_parts.append(part)
            else:
                converted_parts.append(part)
        return ''.join(converted_parts)
    
    def sqrt_operation(self):
        if self.current_input and self.current_input != "0":
            try:
                val = float(self.current_input)
                if val < 0:
                    self.display_var.set("错误")
                    return
                result = sqrt(val)
                
                self.full_expression = f"√({self.current_input})"
                self.expression_var.set(self.full_expression)
                
                if self.binary_mode:
                    result = self.convert_to_binary(result)
                elif result == int(result):
                    result = int(result)
                self.current_input = str(result)
                self.display_var.set(self.current_input)
                self.result_displayed = True
            except:
                self.display_var.set("错误")
    
    def square_operation(self):
        if self.current_input and self.current_input != "0":
            try:
                val = float(self.current_input)
                result = val ** 2
                
                self.full_expression = f"({self.current_input})²"
                self.expression_var.set(self.full_expression)
                
                if self.binary_mode:
                    result = self.convert_to_binary(result)
                elif result == int(result):
                    result = int(result)
                self.current_input = str(result)
                self.display_var.set(self.current_input)
                self.result_displayed = True
            except:
                self.display_var.set("错误")
    
    def mu_operation(self):
        if self.current_input and self.current_input != "0":
            try:
                val = float(self.current_input)
                result = ((val + 100) * val) / 100
                
                self.full_expression = f"MU({self.current_input})"
                self.expression_var.set(self.full_expression)
                
                if self.binary_mode:
                    result = self.convert_to_binary(result)
                elif result == int(result):
                    result = int(result)
                self.current_input = str(result)
                self.display_var.set(self.current_input)
                self.result_displayed = True
            except:
                self.display_var.set("错误")
    
    def toggle_sign(self):
        if self.current_input and self.current_input != "0":
            if self.current_input[0] == '-':
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
            self.display_var.set(self.current_input)
    
    def backspace(self):
        if self.current_input and not self.result_displayed:
            if len(self.current_input) > 1:
                self.current_input = self.current_input[:-1]
            else:
                self.current_input = "0"
            self.display_var.set(self.current_input)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    calc = ModernCalculator()
    calc.run()