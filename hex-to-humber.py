def extract_card_info(hex_string):
    try:
        # Удаляем возможные пробелы и приводим к нижнему регистру
        hex_string = hex_string.replace(" ", "").lower()

        # Проверка длины: должна быть чётной и не менее 14 символов (7 байт), лучше 16 (8 байт)
        if len(hex_string) < 14 or len(hex_string) % 2 != 0:
            return "Ошибка: строка должна содержать как минимум 14–16 hex-символов (7–8 байт)"

        # Преобразуем в массив байтов
        data = bytes.fromhex(hex_string)

        # Проверка достаточности байтов
        if len(data) < 7:
            return "Ошибка: недостаточно байтов для извлечения данных"

        # Извлечение FC и ID
        fc = data[4]
        card_id = (data[5] << 8) | data[6]

        return f"{fc}/{card_id}"
    except Exception as e:
        return f"Ошибка при разборе: {e}"


if __name__ == "__main__":
    while True:
        hex_input = input("Вставьте HEX-строку (или 'exit' для выхода): ").strip()
        if hex_input.lower() == "exit":
            break
        result = extract_card_info(hex_input)
        print("Результат:", result)
