--- parity.lua
local Parity = {}

--- Определение позиций битов контрольных символов в кодовой последовательности
--- @param bits table -- Кодовая последовательность
--- @return table parity_location -- Позиции битов контрольных символов
function Parity.parity_index(bits)
    local bit_index = 2
    local parity_location = {0}

    while bit_index <= #bits do
        table.insert(parity_location, bit_index - 1)
        bit_index = bit_index * 2
    end
    return parity_location
end

--- Определение диапазона битов, для которых нужно вычислить контрольный бит
--- @param bits table -- Кодовая последовательность
--- @param interator integer -- Индексы итератора
--- @return table result -- Диапазон битов
function Parity.parity_range(bits, interator)
    local result = {}
    local next_bit = interator - 1
    local cycle = interator

    -- Получаем позиции контрольных битов
    local parity_positions = Parity.parity_index(bits)

    for index = 1, #bits do
        if index - 1 == next_bit then
            -- Проверяем, не является ли индекс позицией контрольного бита
            local is_parity_bit = false
            for _, parity_pos in ipairs(parity_positions) do
                if index - 1 == parity_pos then
                    is_parity_bit = true
                    break
                end
            end

            if not is_parity_bit then
                table.insert(result, index - 1)
            end

            cycle = cycle - 1
            if cycle == 0 then
                next_bit = next_bit + interator + 1
                cycle = interator
            else
                next_bit = next_bit + 1
            end
        end
    end
    return result
end

--- Вычисление контрольного бита для указанной позиции interator
--- @param bits table -- Кодовая последовательность
--- @param interator integer -- Индексы итератора
--- @return integer result -- Контрольный бит
function Parity.parity(bits, interator)
    local result = 0
    for _, index in ipairs(Parity.parity_range(bits, interator)) do
        result = result + bits[index]
    end
    result = (result % 2 == 0) and 0 or 1
    return result
end

--- Вставка контрольных битов в кодовую последовательность
--- @param bits table -- Кодовая последовательность
--- @return table bits -- Кодовая последовательность с контрольными битами
function Parity.insert_parity(bits)
    for _, bit_index in ipairs(Parity.parity_index(bits)) do
        table.insert(bits, bit_index + 1, 0)
    end
    return bits
end

--- Удаление контрольных битов из кодовой последовательности
--- @param bits table -- Кодовая последовательность
--- @return table result -- Кодовая последовательность без контрольных битов
function Parity.remove_parity(bits)
    local result = {}
    local parity_positions = Parity.parity_index(bits)

    for index, bit in ipairs(bits) do
        local is_parity_bit = false
        for _, parity_pos in ipairs(parity_positions) do
            if index - 1 == parity_pos then
                is_parity_bit = true
                break
            end
        end

        if not is_parity_bit then
            table.insert(result, bit)
        end
    end
    return result
end

--- Вычисление контрольных битов
--- @param bits table -- Кодовая последовательность
--- @return table bits -- Кодовая последовательность с вычисленными контрольными битами
function Parity.calculate_parity(bits)
    for _, bit_index in ipairs(Parity.parity_index(bits)) do
        bits[bit_index + 1] = Parity.parity(bits, bit_index + 1 + 1) -- Учитываем Lua индексацию
    end
    return bits
end

return Parity
