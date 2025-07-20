# RFID Конвертер

Программа для конвертации RFID-кодов между форматами HEX и FC/ID.

![RFID Конвертер](https://github.com/avelender/rfid_converter/raw/main/screenshots/rfid_converter.png)

## Описание

RFID Конвертер — это простая и удобная программа с графическим интерфейсом для конвертации RFID-кодов между двумя форматами:
- **HEX → FC/ID**: преобразование HEX-кода карты в формат FC/ID (например, 6600530072A50101 → 130/09023)
- **FC/ID → HEX**: преобразование кода в формате FC/ID обратно в HEX (например, 130/09023 → 6600530072A50101)

## Возможности

- Мгновенная конвертация при вводе
- Копирование результата в буфер обмена одним кликом
- Вставка из буфера обмена через Ctrl+V или правый клик мыши (работает с любой раскладкой клавиатуры)
- Компактный и интуитивно понятный интерфейс
- Не требует установки

## Скачать

Готовый .exe файл можно скачать из раздела [Releases](https://github.com/avelender/rfid_converter/releases).

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
