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

        return f"{fc}/{card_id}"
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


if __name__ == "__main__":
    while True:
        print("\nВыберите режим:")
        print("1 — Перевести из HEX в FC/ID")
        print("2 — Перевести из FC/ID в HEX")
        print("0 — Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            hex_input = input("Введите HEX (например 6600530072A50101): ").strip()
            print("Результат:", hex_to_fc_id(hex_input))

        elif choice == "2":
            fcid_input = input("Введите FC/ID (например 114/42241): ").strip()
            print("HEX:", fc_id_to_hex(fcid_input))

        elif choice == "0":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Введите 1, 2 или 0.")
