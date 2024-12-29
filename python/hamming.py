from parity import *


def find_error(bits):
    # создаем список, в который будут добавляться индексы битов, которые содержат ошибку
    error_index = []
    # считаем проверочные биты
    check_bits = calculate_parity(bits.copy())
    # print(f"-->check_bits: {check_bits}")

    # проходимся по всем битам
    for index in range(len(bits)):
        # если бит не равен проверочному биту, добавляем индекс в список ошибок
        if bits[index] != check_bits[index]:
            error_index.append(index)
    return error_index


def correct_error(bits, error_index):
    # вычисляем позицию ошибки
    error_position = 0

    for index in error_index:
        error_position += index + 1
    # исправляем ошибочный бит
    bits[error_position - 1] = 0 if bits[error_position - 1] == 1 else 1
    return bits


def hamming_code(bits):
    bits = bits.copy()

    # добавляем проверочные биты
    bits = insert_parity(bits)
    # считаем проверочные биты
    bits = calculate_parity(bits)
    return bits


def hamming_decode(bits):
    bits = bits.copy()
    # находим ошибки в битах
    error_index = find_error(bits)

    # если есть ошибки, исправляем их
    if len(error_index) != 0:
        bits = correct_error(bits, error_index)

    # удаляем проверочные биты
    bits = remove_parity(bits)
    return bits
