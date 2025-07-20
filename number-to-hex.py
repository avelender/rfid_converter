def encode_card(fc_id_str):
    try:
        # Разбиваем ввод по /
        parts = fc_id_str.strip().split("/")
        if len(parts) != 2:
            return "Ошибка: используйте формат FC/ID, например 114/42241"

        fc = int(parts[0])
        card_id = int(parts[1])

        if not (0 <= fc <= 255 and 0 <= card_id <= 65535):
            return "Ошибка: FC должен быть от 0 до 255, а ID — от 0 до 65535"

        # Составляем байтовую структуру:
        data = bytearray()
        data += bytes.fromhex("66005300")     # фиксированное начало
        data.append(fc)                       # байт FC
        data.append((card_id >> 8) & 0xFF)    # старший байт ID
        data.append(card_id & 0xFF)           # младший байт ID
        data.append(0x01)                     # фиксированный конец

        return data.hex().upper()

    except Exception as e:
        return f"Ошибка: {e}"


if __name__ == "__main__":
    while True:
        user_input = input("Введите номер карты (например 114/42241), или 'exit': ").strip()
        if user_input.lower() == "exit":
            break
        result = encode_card(user_input)
        print("HEX:", result)
