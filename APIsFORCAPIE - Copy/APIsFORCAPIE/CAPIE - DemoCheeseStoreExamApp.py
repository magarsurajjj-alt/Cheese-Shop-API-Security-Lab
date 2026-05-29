import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import random

BASE_URL = 'http://localhost:5107'
EMOJIS = ['🧀', '🥖', '🍇', '🍷']

class CheeseAPITester(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('🧀 Cheese Inventory API Tester 🧀')
        self.geometry('800x600')
        self.token = None

        self.create_login_frame()
        self.create_main_frame()

        self.login_frame.pack(fill='both', expand=True)

    def create_login_frame(self):
        self.login_frame = ttk.Frame(self, padding=20)
        ttk.Label(self.login_frame, text='🔑 Username:', font=('Arial', 12)).grid(row=0, column=0, pady=5, padx=5)
        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(self.login_frame, text='🔒 Password:', font=('Arial', 12)).grid(row=1, column=0, pady=5, padx=5)
        self.password_entry = ttk.Entry(self.login_frame, show='*', width=30)
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)

        login_btn = ttk.Button(self.login_frame, text='Login 🔑', command=self.login)
        login_btn.grid(row=2, column=0, pady=10)
        register_btn = ttk.Button(self.login_frame, text='Register 📝', command=self.register)
        register_btn.grid(row=2, column=1, pady=10)

    def create_main_frame(self):
        self.main_frame = ttk.Frame(self, padding=10)

        # Buttons for tests
        btn_frame = ttk.LabelFrame(self.main_frame, text='🛠️ Actions', padding=10)
        btn_frame.pack(fill='x', pady=10, padx=10)

        ttk.Button(btn_frame, text='List Cheeses 🧀', command=self.list_cheeses).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text='Add Cheese ➕', command=self.add_cheese_dialog).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text='Get Cheese 🔍', command=self.get_cheese_dialog).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text='Update Cheese ✏️', command=self.update_cheese_dialog).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text='Sell Cheese 💰', command=self.sell_cheese_dialog).grid(row=0, column=4, padx=5)

        # Response display
        self.response_box = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=15, font=('Courier', 10))
        self.response_box.pack(fill='both', expand=True, padx=10, pady=10)

        # Emoji display for added cheese
        self.emoji_display = ttk.Label(self.main_frame, text='', font=('Arial', 64))
        self.emoji_display.pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            r = requests.post(f"{BASE_URL}/login", json={'username': username, 'password': password})
            if r.status_code == 200:
                self.token = r.json().get('token')
                messagebox.showinfo('Success', '🔓 Logged in successfully')
                self.login_frame.pack_forget()
                self.main_frame.pack(fill='both', expand=True)
            else:
                messagebox.showerror('Error', f"❌ {r.text}")
        except Exception as e:
            messagebox.showerror('Error', f"❌ {e}")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            r = requests.post(f"{BASE_URL}/register", json={'username': username, 'password': password})
            if r.status_code == 200:
                messagebox.showinfo('Success', '✅ Registered successfully')
            else:
                messagebox.showerror('Error', f"❌ {r.text}")
        except Exception as e:
            messagebox.showerror('Error', f"❌ {e}")

    def make_auth_headers(self):
        return {'Authorization': f'Bearer {self.token}'}

    def list_cheeses(self):
        try:
            r = requests.get(f"{BASE_URL}/cheeses", headers=self.make_auth_headers())
            self.display_response(r)
        except Exception as e:
            self.response_box.insert(tk.END, f"Error: {e}\n")

    def add_cheese_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title('➕ Add Cheese')
        ttk.Label(dlg, text='Name:').grid(row=0, column=0, padx=5, pady=5)
        name_e = ttk.Entry(dlg); name_e.grid(row=0, column=1)
        ttk.Label(dlg, text='Description:').grid(row=1, column=0, padx=5, pady=5)
        desc_e = ttk.Entry(dlg); desc_e.grid(row=1, column=1)
        ttk.Label(dlg, text='Price:').grid(row=2, column=0, padx=5, pady=5)
        price_e = ttk.Entry(dlg); price_e.grid(row=2, column=1)
        ttk.Label(dlg, text='Stock:').grid(row=3, column=0, padx=5, pady=5)
        stock_e = ttk.Entry(dlg); stock_e.grid(row=3, column=1)
        def submit():
            data = {
                'name': name_e.get(), 'description': desc_e.get(),
                'price': float(price_e.get()), 'stock': int(stock_e.get())
            }
            r = requests.post(f"{BASE_URL}/cheeses", headers=self.make_auth_headers(), json=data)
            self.display_response(r)
            # Show a random emoji
            self.emoji_display.config(text=random.choice(EMOJIS))
            dlg.destroy()
        ttk.Button(dlg, text='Submit', command=submit).grid(row=4, column=0, columnspan=2, pady=10)

    def get_cheese_dialog(self):
        dlg = tk.Toplevel(self); dlg.title('🔍 Get Cheese')
        ttk.Label(dlg, text='Cheese ID:').grid(row=0, column=0, padx=5)
        id_e = ttk.Entry(dlg); id_e.grid(row=0, column=1)
        def submit():
            cid = id_e.get()
            r = requests.get(f"{BASE_URL}/cheeses/{cid}", headers=self.make_auth_headers())
            self.display_response(r)
            dlg.destroy()
        ttk.Button(dlg, text='Get', command=submit).grid(row=1, column=0, columnspan=2, pady=10)

    def update_cheese_dialog(self):
        dlg = tk.Toplevel(self); dlg.title('✏️ Update Cheese')
        ttk.Label(dlg, text='Cheese ID:').grid(row=0, column=0, padx=5)
        id_e = ttk.Entry(dlg); id_e.grid(row=0, column=1)
        ttk.Label(dlg, text='Field:').grid(row=1, column=0)
        field_cb = ttk.Combobox(dlg, values=['name', 'description', 'price', 'stock']); field_cb.grid(row=1, column=1)
        ttk.Label(dlg, text='New Value:').grid(row=2, column=0)
        val_e = ttk.Entry(dlg); val_e.grid(row=2, column=1)
        def submit():
            payload = {field_cb.get():
                       float(val_e.get()) if field_cb.get()=='price' else int(val_e.get()) if field_cb.get()=='stock' else val_e.get()}
            r = requests.put(f"{BASE_URL}/cheeses/{id_e.get()}", headers=self.make_auth_headers(), json=payload)
            self.display_response(r)
            dlg.destroy()
        ttk.Button(dlg, text='Update', command=submit).grid(row=3, column=0, columnspan=2, pady=10)

    def sell_cheese_dialog(self):
        dlg = tk.Toplevel(self); dlg.title('💰 Sell Cheese')
        ttk.Label(dlg, text='Cheese ID:').grid(row=0, column=0)
        id_e = ttk.Entry(dlg); id_e.grid(row=0, column=1)
        ttk.Label(dlg, text='Quantity:').grid(row=1, column=0)
        qty_e = ttk.Entry(dlg); qty_e.grid(row=1, column=1)
        def submit():
            payload = {'quantity': int(qty_e.get())}
            r = requests.post(f"{BASE_URL}/cheeses/{id_e.get()}/sell", headers=self.make_auth_headers(), json=payload)
            self.display_response(r)
            dlg.destroy()
        ttk.Button(dlg, text='Sell', command=submit).grid(row=2, column=0, columnspan=2, pady=10)

    def display_response(self, response):
        try:
            body = response.json()
            txt = json.dumps(body, indent=2)
        except:
            txt = response.text
        text = f"{response.status_code} \n{txt}\n{'-'*60}\n"
        self.response_box.insert(tk.END, text)
        self.response_box.see(tk.END)

if __name__ == '__main__':
    app = CheeseAPITester()
    app.mainloop()
