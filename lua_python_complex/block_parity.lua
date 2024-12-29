-- block_parity.lua
local BlockParity = {}

--- Кодирование сообщения блочным кодом с проверкой на четность
--- @param message string -- Сообщение для кодирования
--- @return string -- Закодированное сообщение
function BlockParity.block_encode(message)
    print("in block encode")
    print("message", message)
    local encoded_blocks = {}
    -- Разбиваем сообщение на блоки по 8 бит
    for i = 1, #message, 8 do
        local block = message:sub(i, i + 7)
        -- Вычисляем бит четности
        local parity_bit = #block:gsub("0", "") % 2
        -- Добавляем бит четности в начало блока
        table.insert(encoded_blocks, tostring(parity_bit) .. block)
    end
    -- Объединяем закодированные блоки в одну строку
    return table.concat(encoded_blocks)
end

--- Декодирование сообщения блочным кодом с проверкой на четность
--- @param encoded_message string -- Закодированное сообщение
--- @return string -- Декодированное сообщение
function BlockParity.block_decode(encoded_message)
    local decoded_blocks = {}
    for i = 1, #encoded_message, 9 do
        local block = encoded_message:sub(i, i + 8)
        -- извлекаем бит четности
        local parity_bit = tonumber(block:sub(1, 1))
        -- извлекаем данные блока
        local data_block = block:sub(2)
        -- Проверяем, правильно ли закодирован блок
        if (#data_block:gsub("0", "") % 2) == parity_bit then
            -- Если блок закодирован правильно, добавляем его к результату
            table.insert(decoded_blocks, data_block)
        else
            -- Если блок закодирован неправильно, выбрасываем ошибку
            error("Ошибка декодирования: блок закодирован неправильно")
        end
    end
    return table.concat(decoded_blocks)
end

return BlockParity
