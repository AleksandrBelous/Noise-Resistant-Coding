def parity_index(bits):
    # определение позиций битов контрольных символов в кодовой последовательности
    bit_index = 2
    parity_location = [0]

    while bit_index <= len(bits):
        parity_location.append(bit_index - 1)
        bit_index = bit_index * 2
    return parity_location


def parity_range(bits, interator):
    # определение диапазона битов, для которых нужно вычислить контрольный бит
    result = []
    next_bit = interator - 1
    cycle = interator

    for index, bit in enumerate(bits):
        if index == next_bit:
            if index not in parity_index(bits):
                result.append(index)
            cycle -= 1

            if cycle == 0:
                next_bit += interator + 1
                cycle = interator
            else:
                next_bit += 1
    return result


def parity(bits, interator):
    # вычисление контрольного бита для указанной позиции interator
    result = 0
    for index in parity_range(bits, interator):
        result += bits[index]
    return 0 if result % 2 == 0 else 1


def insert_parity(bits):
    # вставка контрольных битов в кодовую последовательность
    for bit_index in parity_index(bits):
        # print(f"bit_index: {bit_index}")
        bits.insert(bit_index, 0)
    return bits


def remove_parity(bits):
    # удаление контрольных битов из кодовой последовательности
    result = []
    for index, bit in enumerate(bits):
        if index not in parity_index(bits):
            result.append(bit)
    return result


def calculate_parity(bits):
    # вычисление контрольных битов
    for bit_index in parity_index(bits):
        # print(f"bit_index: {bit_index}")
        bits[bit_index] = parity(bits, bit_index + 1)
    return bits
