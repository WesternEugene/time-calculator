import customtkinter as ctk
import datetime
import threading
import pystray
from PIL import Image, ImageDraw
import winreg
import os
import ctypes
import sys

# Setup window
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_tray_icon():
    try:
        image = Image.open(resource_path("icon.ico"))
    except Exception:
        # Создаем простую иконку для трея
        image = Image.new('RGB', (64, 64), color=(31, 106, 165))
        d = ImageDraw.Draw(image)
        d.text((12, 20), "Time", fill=(255, 255, 255))
    return image

class TimeCalculatorApp(ctk.CTk):
    def __init__(self):
        # Делаем базовый фон окна цвета #000001, чтобы потом сделать его прозрачным
        super().__init__(fg_color="#000001")

        self.title("Калькулятор Времени")
        self.geometry("450x620")
        self.resizable(False, False)
        
        # Делаем окно виджетом (без рамки)
        self.overrideredirect(True)
        # Убираем фон (все, что цвета #000001, станет прозрачным)
        self.attributes("-transparentcolor", "#000001")
        
        # Гарантированно убираем из панели задач через 100 мс после создания окна
        self.after(100, self._hide_from_taskbar)

        self.grid_columnconfigure(0, weight=1)

        # --- Custom Title Bar ---
        self.title_bar = ctk.CTkFrame(self, height=35, corner_radius=10, fg_color=("gray85", "gray15"))
        self.title_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

        self.title_label = ctk.CTkLabel(self.title_bar, text=" Калькулятор Времени", font=ctk.CTkFont(size=14, weight="bold"))
        self.title_label.pack(side="left", padx=10)
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)

        self.close_btn = ctk.CTkButton(self.title_bar, text="×", width=35, height=35, corner_radius=10, 
                                       fg_color="transparent", hover_color="red", command=self.hide_to_tray)
        self.close_btn.pack(side="right")

        # --- Start Time Frame ---
        self.start_frame = ctk.CTkFrame(self, corner_radius=15)
        self.start_frame.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="ew")
        self.start_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.start_label = ctk.CTkLabel(self.start_frame, text="Начальное время", font=ctk.CTkFont(size=16, weight="bold"))
        self.start_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.sync_var = ctk.BooleanVar(value=True)
        self.sync_switch = ctk.CTkSwitch(self.start_frame, text="Авто-время", variable=self.sync_var, command=self.toggle_sync)
        self.sync_switch.grid(row=0, column=2, columnspan=2, pady=10, sticky="e", padx=10)

        now = datetime.datetime.now()

        self.date_entry = ctk.CTkEntry(self.start_frame, placeholder_text="ДД.ММ.ГГГГ", justify="center")
        self.date_entry.insert(0, now.strftime("%d.%m.%Y"))
        self.date_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.time_entry = ctk.CTkEntry(self.start_frame, placeholder_text="ЧЧ:ММ", justify="center")
        self.time_entry.insert(0, now.strftime("%H:%M"))
        self.time_entry.grid(row=1, column=2, columnspan=2, padx=10, pady=10, sticky="ew")


        # --- Add/Subtract Frame ---
        self.add_frame = ctk.CTkFrame(self, corner_radius=15)
        self.add_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.add_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.add_label = ctk.CTkLabel(self.add_frame, text="Прибавить / Отнять (можно с минусом)", font=ctk.CTkFont(size=14))
        self.add_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Days
        self.days_label = ctk.CTkLabel(self.add_frame, text="Дни:")
        self.days_label.grid(row=1, column=0, padx=10, pady=(0, 5))
        self.days_entry = ctk.CTkEntry(self.add_frame, justify="center")
        self.days_entry.insert(0, "0")
        self.days_entry.grid(row=2, column=0, padx=10, pady=(0, 10))

        # Hours
        self.hours_label = ctk.CTkLabel(self.add_frame, text="Часы:")
        self.hours_label.grid(row=1, column=1, padx=10, pady=(0, 5))
        self.hours_entry = ctk.CTkEntry(self.add_frame, justify="center")
        self.hours_entry.insert(0, "0")
        self.hours_entry.grid(row=2, column=1, padx=10, pady=(0, 10))

        # Minutes
        self.minutes_label = ctk.CTkLabel(self.add_frame, text="Минуты:")
        self.minutes_label.grid(row=1, column=2, padx=10, pady=(0, 5))
        self.minutes_entry = ctk.CTkEntry(self.add_frame, justify="center")
        self.minutes_entry.insert(0, "0")
        self.minutes_entry.grid(row=2, column=2, padx=10, pady=(0, 10))


        # --- Action Buttons ---
        self.calc_button = ctk.CTkButton(self, text="Рассчитать", font=ctk.CTkFont(size=16, weight="bold"), command=self.calculate)
        self.calc_button.grid(row=3, column=0, padx=20, pady=15, ipadx=10, ipady=5)


        # --- Result Frame ---
        self.result_frame = ctk.CTkFrame(self, corner_radius=15)
        self.result_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        
        self.result_label = ctk.CTkLabel(self.result_frame, text="Результат:", font=ctk.CTkFont(size=16))
        self.result_label.pack(pady=5)
        
        self.result_value = ctk.CTkLabel(self.result_frame, text="--.--.---- --:--", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1f6aa5")
        self.result_value.pack()

        # Error label
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=5, column=0, padx=20, pady=0)
        
        # Переменные для перетаскивания окна
        self._drag_data = {"x": 0, "y": 0}
        
        # Настройка системного трея
        self.tray_icon = None
        self.setup_tray()
        
        # Запускаем часы
        self.update_clock()

    def toggle_sync(self):
        if self.sync_var.get():
            self.update_clock()
            
    def update_clock(self):
        if self.sync_var.get():
            now = datetime.datetime.now()
            
            self.date_entry.delete(0, 'end')
            self.date_entry.insert(0, now.strftime("%d.%m.%Y"))
            
            self.time_entry.delete(0, 'end')
            self.time_entry.insert(0, now.strftime("%H:%M:%S"))
            
            self.after(1000, self.update_clock)

    def start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def do_move(self, event):
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.geometry(f"+{x}+{y}")

    def _hide_from_taskbar(self):
        try:
            hwnd = int(self.wm_frame(), 16)
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_APPWINDOW
            style = style | WS_EX_TOOLWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception as e:
            pass

    def hide_to_tray(self):
        self.withdraw() # Скрыть окно

    def show_from_tray(self, icon, item):
        self.after(0, self._restore_window)
        
    def _restore_window(self):
        self.deiconify()
        self.state('normal')
        
        # Снова применяем скрытие из панели задач на случай, если Windows его вернула
        self._hide_from_taskbar()
        
        try:
            # Принудительно восстанавливаем окно через WinAPI
            ctypes.windll.user32.ShowWindow(int(self.wm_frame(), 16) if sys.platform == 'win32' else self.winfo_id(), 9)
        except Exception:
            pass
            
        self.lift()
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)
        
    def exit_app(self, icon, item):
        icon.stop()
        self.after(0, self.destroy)

    def setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem('Показать виджет', self.show_from_tray, default=True),
            pystray.MenuItem('Запускать с Windows', self.toggle_autostart_tray, checked=lambda item: self.check_autostart()),
            pystray.MenuItem('Выход', self.exit_app)
        )
        self.tray_icon = pystray.Icon("TimeCalc", create_tray_icon(), "Калькулятор Времени", menu)
        # Запускаем трей в отдельном потоке, чтобы не блокировать интерфейс
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def toggle_autostart_tray(self, icon, item):
        current = self.check_autostart()
        self.toggle_autostart(not current)

    def toggle_autostart(self, enable):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "TimeCalculatorWidget"
        
        # Используем pythonw для запуска без консоли
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        script_path = os.path.abspath(__file__)
        command = f'"{python_exe}" "{script_path}"'
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            self.error_label.configure(text=f"Ошибка автозапуска: {e}")

    def check_autostart(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "TimeCalculatorWidget"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False

    def calculate(self):
        self.error_label.configure(text="")
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()
        
        try:
            try:
                start_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M:%S")
            except ValueError:
                start_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
        except ValueError:
            self.error_label.configure(text="Ошибка формата! Используйте ДД.ММ.ГГГГ и ЧЧ:ММ[:СС]")
            return
            
        try:
            days = float(self.days_entry.get() or 0)
            hours = float(self.hours_entry.get() or 0)
            minutes = float(self.minutes_entry.get() or 0)
        except ValueError:
            self.error_label.configure(text="Ошибка значений! Вводите только числа.")
            return
            
        delta = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        result_dt = start_dt + delta
        
        self.result_value.configure(text=result_dt.strftime("%d.%m.%Y %H:%M:%S"))

        if ctk.get_appearance_mode() == "Dark":
            self.result_value.configure(text_color="#63b6f2")
        else:
            self.result_value.configure(text_color="#1f6aa5")

if __name__ == "__main__":
    app = TimeCalculatorApp()
    app.mainloop()
