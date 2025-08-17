import tkinter as tk
from tkinter import ttk, messagebox, font
try:
    from ttkthemes import ThemedTk
except Exception:
    ThemedTk = None

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

# Словарь для хранения префиксов для каждой карты
card_prefixes = {}

def hex_to_fc_id(hex_string):
    try:
        # Удаляем пробелы и приводим к нижнему регистру
        hex_string = hex_string.replace(" ", "").lower()

        # Проверяем длину и четность
        if len(hex_string) < 16:
            return "Ошибка: строка должна содержать минимум 16 hex-символов (8 байт)"
        
        if len(hex_string) % 2 != 0:
            return "Ошибка: количество hex-символов должно быть четным"

        # Проверяем, что строка содержит только HEX-символы
        if not all(c in '0123456789abcdef' for c in hex_string):
            return "Ошибка: строка содержит недопустимые символы (0-9, a-f)"

        try:
            data = bytes.fromhex(hex_string)
        except ValueError:
            return "Ошибка: неверный формат HEX-строки"

        if len(data) < 8:
            return "Ошибка: недостаточно байтов для разбора (минимум 8 байт)"

        # Сохраняем префикс (первые 4 байта)
        prefix = hex_string[:8]
        
        # Универсальная формула конвертации
        # Байт 5 (0-индексированный) - это FC (Facility Code)
        # Байты 6-7 - это ID карты (2 байта)
        fc = data[4]
        card_id = (data[5] << 8) | data[6]
        
        # Форматируем FC и ID с ведущими нулями (FC - 3 цифры, ID - 5 цифр)
        card_key = f"{fc:03d}/{card_id:05d}"
        
        # Сохраняем префикс для этой карты
        card_prefixes[card_key] = prefix
        
        return card_key
    except Exception as e:
        return f"Ошибка при разборе HEX: {e}"


def fc_id_to_hex(fc_id_str):
    try:
        # Проверяем формат ввода
        fc_id_str = fc_id_str.strip()
        if '/' not in fc_id_str:
            return "Ошибка: используйте формат FC/ID, например 114/42241"
        
        parts = fc_id_str.split("/")
        if len(parts) != 2:
            return "Ошибка: используйте формат FC/ID, например 114/42241"

        # Проверяем, что введены числа
        try:
            fc = int(parts[0])
        except ValueError:
            return "Ошибка: FC должен быть числом"
            
        try:
            card_id = int(parts[1])
        except ValueError:
            return "Ошибка: ID должен быть числом"

        # Проверяем диапазоны
        if not (0 <= fc <= 255):
            return "Ошибка: FC должен быть в диапазоне 0–255"
            
        if not (0 <= card_id <= 65535):
            return "Ошибка: ID должен быть в диапазоне 0–65535"
        
        # Форматируем ключ для поиска в словаре
        card_key = f"{fc:03d}/{card_id:05d}"
        
        # Используем сохраненный префикс, если он есть
        prefix = card_prefixes.get(card_key)
        
        # Если префикс не найден, используем универсальный префикс
        if prefix is None:
            # Для всех карт используем стандартный префикс XX003300
            # Где XX зависит от номера карты
            # Используем хеш-функцию для стабильности префикса
            hash_value = (fc * 256 + card_id) % 192 + 32  # Диапазон 32-224 (0x20-0xE0)
            prefix = f"{hash_value:02X}003300"

        # Универсальная формула конвертации
        # Собираем данные в формате XXXXXXXX YY ZZZZ 01
        # Где XXXXXXXX - префикс, YY - FC, ZZZZ - ID, 01 - фиксированный байт
        data = bytearray()
        data += bytes.fromhex(prefix)            # префикс (4 байта)
        data.append(fc)                          # FC (1 байт)
        data.append((card_id >> 8) & 0xFF)       # старший байт ID
        data.append(card_id & 0xFF)              # младший байт ID
        data.append(0x01)                        # фиксированный байт

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
        github_link = ttk.Label(status_frame, text="Github", foreground="blue", cursor="hand2", padding=(2, 1))
        github_link.pack(side=tk.RIGHT, padx=2)
        github_link.bind("<Button-1>", lambda e: self.open_url(github_url))
        
        # Создаем простой шрифт с подчеркиванием
        link_font = font.Font(family="TkDefaultFont", size=8)
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
        
        buttons_frame = ttk.Frame(result_frame)
        buttons_frame.pack(side=tk.LEFT)
        
        copy_btn = ttk.Button(buttons_frame, text="Копировать", command=lambda: self.copy_to_clipboard(self.fcid_result['text']))
        copy_btn.pack(side=tk.LEFT, padx=2)
        
        clear_btn = ttk.Button(buttons_frame, text="Очистить", command=lambda: self.clear_hex_input())
        clear_btn.pack(side=tk.LEFT, padx=2)

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
        
        buttons_frame = ttk.Frame(result_frame)
        buttons_frame.pack(side=tk.LEFT)
        
        copy_btn = ttk.Button(buttons_frame, text="Копировать", command=lambda: self.copy_to_clipboard(self.hex_result['text']))
        copy_btn.pack(side=tk.LEFT, padx=2)
        
        clear_btn = ttk.Button(buttons_frame, text="Очистить", command=lambda: self.clear_fcid_input())
        clear_btn.pack(side=tk.LEFT, padx=2)

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
        if len(hex_input) >= 16 and len(hex_input) % 2 == 0:
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
    
    def clear_hex_input(self):
        """Clear HEX input field and result"""
        self.hex_input.delete(0, tk.END)
        self.fcid_result['text'] = ""
        self.status_var.set("Поле HEX очищено")
    
    def clear_fcid_input(self):
        """Clear FC/ID input field and result"""
        self.fcid_input.delete(0, tk.END)
        self.hex_result['text'] = ""
        self.status_var.set("Поле FC/ID очищено")
    

if __name__ == "__main__":
    # Используем ThemedTk для красивой темы, если доступен
    if ThemedTk is not None:
        root = ThemedTk(theme="arc")  # Можно выбрать другие темы: "arc", "equilux", "breeze" и т.д.
    else:
        # Если ttkthemes недоступен, используем обычный Tk
        root = tk.Tk()
        
    # Вставка обрабатывается непосредственно в PasteEntry
        
    app = RFIDConverterApp(root)
    
    # Центрируем окно на экране
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()
