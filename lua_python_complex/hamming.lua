--- hamming.lua
local Hamming = {}

local parity = require "parity"

--- Находит ошибочные биты в последовательности
--- @param bits table -- Кодовая последовательность
--- @return table error_index -- Индексы ошибочных битов
function Hamming.find_error(bits)
    local error_index = {}
    local check_bits = parity.calculate_parity(bits) -- Вычисляем контрольные биты

    -- Сравниваем каждый бит с контрольными битами
    for i = 1, #bits do
        if bits[i] ~= check_bits[i] then
            table.insert(error_index, i)
        end
    end
    return error_index
end

--- Исправляет ошибки в последовательности
--- @param bits table -- Кодовая последовательность
--- @param error_index table -- Индексы ошибочных битов
--- @return table bits -- Исправленная последовательность
function Hamming.correct_error(bits, error_index)
    local error_position = 0

    -- Вычисляем позицию ошибки
    for _, index in ipairs(error_index) do
        error_position = error_position + index
    end

    -- Исправляем ошибочный бит
    if error_position > 0 then
        bits[error_position] = 1 - bits[error_position]
    end
    return bits
end

--- Кодирование Хэмминга
--- @param bits table -- Исходная последовательность
--- @return table bits -- Закодированная последовательность
function Hamming.hamming_code(bits)
    print("in hamming code", type(bits), #bits)
    for i = 1, #bits do
        print(bits[i])
    end
    local bits_copy = {table.unpack(bits)}

    -- Добавляем контрольные биты
    bits_copy = parity.insert_parity(bits_copy)
    -- Вычисляем значения контрольных битов
    bits_copy = parity.calculate_parity(bits_copy)
    print("in hamming code and bits_copy", type(bits_copy), #bits_copy)
    for i = 1, #bits_copy do
        print(bits_copy[i])
    end
    return table.unpack(bits_copy)
end

--- Декодирование Хэмминга
--- @param bits table -- Закодированная последовательность
--- @return table bits -- Декодированная последовательность
function Hamming.hamming_decode(bits)
    local bits_copy = {table.unpack(bits)}

    -- Находим ошибки в последовательности
    local error_index = Hamming.find_error(bits_copy)

    -- Исправляем ошибки, если они есть
    if #error_index > 0 then
        bits_copy = Hamming.correct_error(bits_copy, error_index)
    end

    -- Удаляем контрольные биты
    bits_copy = parity.remove_parity(bits_copy)
    return table.unpack(bits_copy)
end

return Hamming
