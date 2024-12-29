def block_encode(message):
    """Кодирование сообщения блочным кодом с проверкой на четность"""
    # Разбиваем сообщение на блоки по 8 бит
    blocks = [message[i:i + 8] for i in range(0, len(message), 8)]

    encoded_blocks = []
    for block in blocks:
        # Вычисляем бит четности
        parity_bit = str(block.count('1') % 2)
        # Добавляем бит четности в начало блока
        encoded_block = parity_bit + block
        encoded_blocks.append(encoded_block)

    # Объединяем закодированные блоки в одну строку
    encoded_message = ''.join(encoded_blocks)
    return encoded_message


def block_decode(encoded_message):
    """Декодирование сообщения, закодированного блочным кодом с проверкой на четность"""
    decoded_blocks = []
    for i in range(0, len(encoded_message), 9):
        # Извлекаем бит четности и блок данных из закодированного блока
        parity_bit, block = encoded_message[i], encoded_message[i + 1:i + 9]
        # Проверяем, правильно ли закодирован блок
        if str(block.count('1') % 2) == parity_bit:
            # Если блок закодирован правильно, удаляем бит четности и сохраняем блок данных
            decoded_blocks.append(block[0:])
        else:
            # Если блок закодирован неправильно, генерируем ошибку и завершаем декодирование
            raise ValueError("Ошибка декодирования: блок закодирован неправильно")

    # Объединяем декодированные блоки в одну строку
    decoded_message = ''.join(decoded_blocks)
    return decoded_message


# etel = encode("0000000110000001")
# decode(etel)
