# RFID Конвертер

Болид (обоссанный) записывает в своих поделиях коды бесконтактных меток EM-Marine, шифруя известным алгоритмом, из-за чего становится проблематично добавить метку ко коду удаленно, не прикладывая ее к считывателю. И вот долгожданный релиз программы, облегчающей эту задачу 

![RFID Конвертер](https://github.com/avelender/rfid_converter/raw/main/screen.png)

## Описание

RFID Конвертер — это простая и удобная программа с графическим интерфейсом для конвертации RFID-кодов между двумя форматами:
- **HEX → FC/ID**: преобразование HEX-кода карты в формат FC/ID (например, 6600530072A50101 → 130/09023)
- **FC/ID → HEX**: преобразование кода в формате FC/ID обратно в HEX (например, 130/09023 → 6600530072A50101)

## Скачать

[Releases](https://github.com/avelender/rfid_converter/releases)

## Запуск из исходного кода

### Требования
- Python 3.6 или выше
- Библиотеки: tkinter, ttkthemes

### Установка зависимостей
```bash
pip install ttkthemes
```

### Запуск
```bash
python rfid_converter_gui.py
```

## Сборка .exe файла

Для сборки исполняемого файла используется PyInstaller:

```bash
pip install pyinstaller
pyinstaller --windowed --onefile rfid_converter_gui.py
```

Готовый .exe файл будет находиться в папке `dist`.

## Лицензия

[MIT](https://opensource.org/licenses/MIT)
