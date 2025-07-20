import tkinter as tk
from tkinter import ttk, messagebox, font
import re
import sys
from ttkthemes import ThemedTk

# Создаем свой класс Entry с поддержкой Ctrl+V независимо от раскладки
class PasteEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        self.callback = kwargs.pop('paste_callback', None)
        super().__init__(master, **kwargs)
        
        # Биндим правую кнопку мыши для контекстного меню
        self.bind('<Button-3>', self.show_menu)
        
        # Биндим Ctrl+V независимо от раскладки (по коду клавиши)
        # 86 - код клавиши V на любой раскладке
        self.bind('<Control-KeyPress>', self._ctrl_key_handler)
        
        # Создаем контекстное меню
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Вставить", command=self.paste)
    
    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)
    
    def _ctrl_key_handler(self, event):
        # Проверяем код клавиши (86 = V, 118 = v)
        if event.keycode == 86 or event.keycode == 118:
            self.paste()
            return "break"  # Останавливаем дальнейшую обработку события
    
    def paste(self):
        try:
            clipboard = self.clipboard_get()
            if clipboard:
                self.delete(0, tk.END)
                self.insert(0, clipboard)
                if self.callback:
                    self.callback()
        except Exception as e:
            print(f"Ошибка при вставке: {e}")

def hex_to_fc_id(hex_string):
    try:
        hex_string = hex_string.replace(" ", "").lower()

        if len(hex_string) < 14 or len(hex_string) % 2 != 0:
            return "Ошибка: строка должна содержать минимум 14–16 hex-символов (7–8 байт)"

        data = bytes.fromhex(hex_string)

        if len(data) < 7:
            return "Ошибка: недостаточно байтов для разбора"

        fc = data[4]
        card_id = (data[5] << 8) | data[6]
        
        # Форматируем ID с ведущими нулями (всегда 5 цифр)
        return f"{fc}/{card_id:05d}"
    except Exception as e:
        return f"Ошибка при разборе HEX: {e}"


def fc_id_to_hex(fc_id_str):
    try:
        parts = fc_id_str.strip().split("/")
        if len(parts) != 2:
            return "Ошибка: используйте формат FC/ID, например 114/42241"

        fc = int(parts[0])
        card_id = int(parts[1])

        if not (0 <= fc <= 255 and 0 <= card_id <= 65535):
            return "Ошибка: FC должен быть 0–255, ID — 0–65535"

        data = bytearray()
        data += bytes.fromhex("66005300")       # фиксированная часть
        data.append(fc)                          # FC
        data.append((card_id >> 8) & 0xFF)       # старший байт
        data.append(card_id & 0xFF)              # младший байт
        data.append(0x01)                        # фиксирующий байт

        return data.hex().upper()
    except Exception as e:
        return f"Ошибка при генерации HEX: {e}"


class RFIDConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RFID Конвертер")
        self.root.geometry("400x220")
        self.root.resizable(True, True)
        self.root.minsize(400, 220)
        
        # Создаем основной фрейм
        main_frame = ttk.Frame(root, padding=5)
        main_frame.pack(fill='x')
        
        # Создаем фрейм для HEX -> FC/ID (верхняя часть)
        hex_to_fcid_frame = ttk.LabelFrame(main_frame, text="HEX → FC/ID", padding=2)
        hex_to_fcid_frame.pack(fill='x', pady=(0, 2))
        self.setup_hex_to_fcid_section(hex_to_fcid_frame)
        
        # Создаем фрейм для FC/ID -> HEX (нижняя часть)
        fcid_to_hex_frame = ttk.LabelFrame(main_frame, text="FC/ID → HEX", padding=2)
        fcid_to_hex_frame.pack(fill='x')
        self.setup_fcid_to_hex_section(fcid_to_hex_frame)
        
        # Создаем фрейм для статусной строки с вдавленным видом
        status_frame = ttk.Frame(root, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Статусная строка слева
        self.status_var = tk.StringVar()
        self.status_var.set("Готово к работе")
        self.status_bar = ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W, padding=(2, 1))
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Вертикальный разделитель
        ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=1)
        
        # Ссылка на GitHub справа
        github_url = "https://github.com/avelender/rfid_converter"
        github_link = ttk.Label(status_frame, text=github_url, foreground="blue", cursor="hand2", padding=(2, 1))
        github_link.pack(side=tk.RIGHT, padx=2)
        github_link.bind("<Button-1>", lambda e: self.open_url(github_url))
        
        # Создаем простой шрифт с подчеркиванием
        link_font = font.Font(family="TkDefaultFont", size=7)
        link_font.configure(underline=True)
        github_link.configure(font=link_font)

    def setup_hex_to_fcid_section(self, frame):
        # Используем переданный фрейм вместо создания нового
        
        # Инструкция и поле ввода
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=1)
        
        ttk.Label(input_frame, text="HEX:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 2))
        
        # Поле ввода с поддержкой вставки
        self.hex_input = PasteEntry(input_frame, width=30, font=("Consolas", 9), 
                                  paste_callback=self.on_hex_input_change)
        self.hex_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.hex_input.bind("<KeyRelease>", self.on_hex_input_change)
        
        # Пример
        ttk.Label(frame, text="Пример: 6600530072A50101", font=("Arial", 7)).pack(anchor=tk.W, pady=0)
        
        # Результат
        result_frame = ttk.Frame(frame)
        result_frame.pack(fill=tk.X, pady=1, padx=1)
        
        self.fcid_result = ttk.Label(result_frame, text="", font=("Arial", 10, "bold"))
        self.fcid_result.pack(side=tk.LEFT, padx=2)
        
        copy_btn = ttk.Button(result_frame, text="Копировать", command=lambda: self.copy_to_clipboard(self.fcid_result['text']))
        copy_btn.pack(side=tk.LEFT, padx=2)

    def setup_fcid_to_hex_section(self, frame):
        # Используем переданный фрейм вместо создания нового
        
        # Инструкция и поле ввода
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=1)
        
        ttk.Label(input_frame, text="FC/ID:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 2))
        
        # Поле ввода с поддержкой вставки
        self.fcid_input = PasteEntry(input_frame, width=30, font=("Consolas", 9), 
                                   paste_callback=self.on_fcid_input_change)
        self.fcid_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.fcid_input.bind("<KeyRelease>", self.on_fcid_input_change)
        
        # Пример
        ttk.Label(frame, text="Пример: 130/09023", font=("Arial", 7)).pack(anchor=tk.W, pady=0)
        
        # Результат
        result_frame = ttk.Frame(frame)
        result_frame.pack(fill=tk.X, pady=1, padx=1)
        
        self.hex_result = ttk.Label(result_frame, text="", font=("Consolas", 10, "bold"))
        self.hex_result.pack(side=tk.LEFT, padx=2)
        
        copy_btn = ttk.Button(result_frame, text="Копировать", command=lambda: self.copy_to_clipboard(self.hex_result['text']))
        copy_btn.pack(side=tk.LEFT, padx=2)

    def convert_hex_to_fcid(self):
        hex_input = self.hex_input.get().strip()
        if not hex_input:
            messagebox.showwarning("Предупреждение", "Введите HEX-код карты")
            return
            
        result = hex_to_fc_id(hex_input)
        self.fcid_result['text'] = result
        
        if not result.startswith("Ошибка"):
            self.status_var.set(f"HEX {hex_input} успешно конвертирован в {result}")
        else:
            self.status_var.set(result)

    def convert_fcid_to_hex(self):
        fcid_input = self.fcid_input.get().strip()
        if not fcid_input:
            messagebox.showwarning("Предупреждение", "Введите FC/ID карты")
            return
            
        result = fc_id_to_hex(fcid_input)
        self.hex_result['text'] = result
        
        if not result.startswith("Ошибка"):
            self.status_var.set(f"FC/ID {fcid_input} успешно конвертирован в HEX")
        else:
            self.status_var.set(result)

    def on_hex_input_change(self, event=None):
        # Автоматическая конвертация при вводе
        hex_input = self.hex_input.get().strip()
        if len(hex_input) >= 14:
            result = hex_to_fc_id(hex_input)
            self.fcid_result['text'] = result
            
            if not result.startswith("Ошибка"):
                self.status_var.set(f"HEX {hex_input} успешно конвертирован в {result}")

    def on_fcid_input_change(self, event=None):
        # Автоматическая конвертация при вводе
        fcid_input = self.fcid_input.get().strip()
        if '/' in fcid_input:
            result = fc_id_to_hex(fcid_input)
            self.hex_result['text'] = result
            
            if not result.startswith("Ошибка"):
                self.status_var.set(f"FC/ID {fcid_input} успешно конвертирован в HEX")

    def copy_to_clipboard(self, text):
        if text and not text.startswith("Ошибка"):
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_var.set(f"Результат скопирован в буфер обмена: {text}")
            
    def open_url(self, url):
        """Open URL in default browser"""
        import webbrowser
        webbrowser.open_new(url)
        self.status_var.set("Готово к работе")
        



if __name__ == "__main__":
    try:
        # Используем ThemedTk для красивой темы
        root = ThemedTk(theme="arc")  # Можно выбрать другие темы: "arc", "equilux", "breeze" и т.д.
    except Exception:
        # Если не получилось, используем обычный Tk
        root = tk.Tk()
        
    # Настраиваем обработку вставки для всех платформ
    # Создаем виртуальное событие для вставки
    root.event_add('<<PasteText>>', '<Control-v>', '<Control-V>')
    
    # Добавляем обработчик для всех Entry
    def handle_paste(event):
        try:
            widget = event.widget
            if isinstance(widget, tk.Entry) or isinstance(widget, ttk.Entry):
                clipboard = widget.clipboard_get()
                if clipboard:
                    widget.delete(0, tk.END)
                    widget.insert(0, clipboard)
                    return "break"
        except Exception as e:
            print(f"Ошибка при вставке: {e}")
    
    # Привязываем обработчик к виртуальному событию
    root.bind_class('Entry', '<<PasteText>>', handle_paste)
        
    app = RFIDConverterApp(root)
    
    # Центрируем окно на экране
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()
