--- reedSolo.lua
local ReedSolo = {}

-- Создаем таблицы для логарифмических значений элементов поля Галуа
-- `gf_exp` хранит значения элементов поля Галуа в экспоненциальном представлении,
-- `gf_log` хранит логарифмические значения элементов поля Галуа
ReedSolo.gf_exp = {}
ReedSolo.gf_log = {}

-- Инициализация таблиц значениями 0
for i = 1, 512 do
    ReedSolo.gf_exp[i] = 0
end

for i = 1, 256 do
    ReedSolo.gf_log[i] = 0
end

--- Умножение двух элементов поля Галуа
--- @param x integer -- Элемент поля Галуа
--- @param y integer -- Элемент поля Галуа
--- @return integer -- Результат умножения в поле Галуа
function ReedSolo.gf_mul(x, y)
    if x == 0 or y == 0 then
        return 0
    end
    -- print('in mul',
    -- 'x='..x,
    -- 'y='..y,
    -- 'log[x]='..ReedSolo.gf_log[x + 1],
    -- 'log[y]='..ReedSolo.gf_log[y + 1],
    -- 'sum='..(ReedSolo.gf_log[x + 1] + ReedSolo.gf_log[y + 1]),
    -- 'exp='..ReedSolo.gf_exp[ReedSolo.gf_log[x + 1] + ReedSolo.gf_log[y + 1]] + 1)
    return ReedSolo.gf_exp[(ReedSolo.gf_log[x + 1] + ReedSolo.gf_log[y + 1]) + 1]
end

-- Функция для выполнения побитового XOR без использования ~
local function bitwise_xor(a, b)
    local result = 0
    local bit = 1
    while a > 0 or b > 0 do
        local a_bit = a % 2
        local b_bit = b % 2
        local xor_bit = (a_bit + b_bit) % 2 -- Реализация XOR через сложение по модулю 2
        result = result + xor_bit * bit
        a = math.floor(a / 2)
        b = math.floor(b / 2)
        bit = bit * 2
    end
    return result
end

--- Умножение двух многочленов в поле Галуа
--- @param p integer[] -- Коэффициенты первого многочлена
--- @param q integer[] -- Коэффициенты второго многочлена
--- @return integer[] -- Коэффициенты результирующего многочлена
function ReedSolo.gf_poly_mul(p, q)
    local r = {}
    -- print('length of p: ', #p)
    -- print('length of q: ', #q)
    for i = 1, #p + #q - 1 do
        r[i] = 0
    end
    -- print('length of r: ', #r)

    for j = 0, #q - 1 do
        for i = 0, #p - 1 do
            -- print('j='..j, 'i='..i, 'j+i+1='..i + j + 1, 'r[]='..r[i + j + 1])
            -- print('p[i+1]=', p[i+1])
            -- print('q[j+1]=', q[j+1])
            -- print('will put', ReedSolo.gf_mul(p[i + 1], q[j + 1]))
            --r[i + j + 1] = r[i + j + 1] ~ ReedSolo.gf_mul(p[i + 1], q[j + 1])
            r[i + j + 1] = bitwise_xor(r[i + j + 1], ReedSolo.gf_mul(p[i + 1], q[j + 1]))
            -- print(j, i, i + j + 1, r[i + j + 1])
        end
    end
    return r
end

--- Генерация порождающего многочлена для кода Рида-Соломона
--- @param nsym integer -- Количество символов для кода Рида-Соломона
--- @return integer[] -- Коэффициенты порождающего многочлена
function ReedSolo.rs_generator_poly(nsym)
    local g = {1}
    for i = 0, nsym - 1 do
        -- print('i='..i..'----------')
        -- print('g=')
        -- for i = 1, #g do
        --     print(g[i])
        -- end
        g = ReedSolo.gf_poly_mul(g, {1, ReedSolo.gf_exp[i + 1]})
        -- print('g=')
        -- for i = 1, #g do
        --     print(g[i])
        -- end
        -- print('i='..i..'----------')
    end
    return g
end

--- Кодирование сообщения с использованием кода Рида-Соломона
--- @param msg_in integer[] -- Входное сообщение
--- @param nsym integer -- Количество символов для кодирования
--- @return integer[] -- Закодированное сообщение
function ReedSolo.rs_encode_msg(msg_in, nsym)
    -- Основная функция кодирования Рида-Соломона,
    -- использующая полиномиальное деление (алгоритм расширенного
    -- синтетического деления)

    -- Проверяем, что сообщение не слишком длинное
    -- if (len(msg_in) + nsym) > 255:
    --     raise ValueError("Message is too long (%i when max is 255)" % (len(msg_in) + nsym))

    -- Получаем генераторный полином для Рида-Соломона
    local gen = ReedSolo.rs_generator_poly(nsym)
    local msg_out = {}

    for i = 1, #msg_in + #gen - 1 do
        msg_out[i] = 0
    end

    for i = 1, #msg_in do
        msg_out[i] = msg_in[i]
    end

    for i = 1, #msg_in do
        local coef = msg_out[i]
        if coef ~= 0 then
            for j = 2, #gen do
                -- Поскольку первая цифра многочлена равна 1, (1 ^ 1 == 0), вы можете пропустить
                -- msg_out[i + j - 1] = msg_out[i + j - 1] ~ ReedSolo.gf_mul(gen[j], coef)
                msg_out[i + j - 1] = bitwise_xor(msg_out[i + j - 1], ReedSolo.gf_mul(gen[j], coef))
            end
        end
    end

    for i = 1, #msg_in do
        msg_out[i] = msg_in[i]
    end

    return table.unpack(msg_out)
end

--- Возведение числа в степень в конечном поле Галуа GF(2^8)
--- @param x integer -- Число
--- @param power integer -- Степень
--- @return integer -- Результат возведения в степень
function ReedSolo.gf_pow(x, power)
    return ReedSolo.gf_exp[(ReedSolo.gf_log[x + 1] * power) % 255 + 1]
end

--- Нахождение обратного элемента в конечном поле Галуа GF(2^8)
--- @param x integer -- Число
--- @return integer -- Обратное число
function ReedSolo.gf_inverse(x)
    -- gf_inverse(x) == gf_div(1, x)
    return ReedSolo.gf_exp[255 - ReedSolo.gf_log[x + 1] + 1]
end

--- Вычитание чисел в конечном поле Галуа GF(2^8)
--- @param x integer -- Первое число
--- @param y integer -- Второе число
--- @return integer -- Результат вычитания
function ReedSolo.gf_sub(x, y)
    -- Вычитание двух чисел в поле Галуа GF(2^8)
    -- return x ~ y
    return bitwise_xor(x, y)
end

--- Сложение двух многочленов в конечном поле Галуа GF(2^8)
--- @param p integer[] -- Первый многочлен
--- @param q integer[] -- Второй многочлен
--- @return integer[] -- Результат сложения
function ReedSolo.gf_poly_add(p, q)
    local r = {}
    for i = 1, math.max(#p, #q) do
        r[i] = 0
    end

    for i = 1, #p do
        r[i + #r - #p] = p[i]
    end

    for i = 1, #q do
        -- r[i + #r - #q] = r[i + #r - #q] ~ q[i]
        r[i + #r - #q] = bitwise_xor(r[i + #r - #q], q[i])
    end

    return r
end

--- Вычисление значения многочлена в конечном поле Галуа GF(2^8)
--- @param p integer[] -- Коэффициенты многочлена
--- @param x integer -- Точка, в которой вычисляется значение
--- @return integer -- Результат вычисления
function ReedSolo.gf_poly_eval(p, x)
    local y = p[1]
    for i = 2, #p do
        -- y = ReedSolo.gf_mul(y, x) ~ p[i]
        y = bitwise_xor(y, ReedSolo.gf_mul(y, x))
    end
    return y
end

--- Вычисление синдромов для заданного сообщения
--- @param msg integer[] -- Сообщение
--- @param nsym integer -- Количество символов синдромов
--- @return integer[] -- Синдромы
function ReedSolo.rs_calc_syndromes(msg, nsym)
    local synd = {}
    for i = 1, nsym do
        synd[i] = ReedSolo.gf_poly_eval(msg, ReedSolo.gf_pow(2, i - 1))
    end
    table.insert(synd, 1, 0)
    return synd
end

--- Масштабирование многочлена в поле Галуа GF(2^8)
--- @param p integer[] -- Многочлен
--- @param x integer -- Константа
--- @return integer[] -- Результат масштабирования
function ReedSolo.gf_poly_scale(p, x)
    local r = {}
    for i = 1, #p do
        r[i] = ReedSolo.gf_mul(p[i], x)
    end
    return r
end

--- Деление двух чисел в поле Галуа GF(2^8)
--- @param x integer -- Делимое
--- @param y integer -- Делитель
--- @return integer -- Результат деления
function ReedSolo.gf_div(x, y)
    if y == 0 then error("ZeroDivisionError") end
    if x == 0 then return 0 end
    return ReedSolo.gf_exp[(ReedSolo.gf_log[x] + 255 - ReedSolo.gf_log[y]) % 255 + 1]
end

--- Полиномиальное деление в поле Галуа GF(2^8)
--- @param dividend integer[] -- Делимое
--- @param divisor integer[] -- Делитель
--- @return integer[], integer[] -- Частное, остаток
function ReedSolo.gf_poly_div(dividend, divisor)
    local msg_out = {}
    for i = 1, #dividend do
        msg_out[i] = dividend[i]
    end

    for i = 1, #dividend - (#divisor - 1) do
        local coef = msg_out[i]
        if coef ~= 0 then
            for j = 2, #divisor do
                if divisor[j] ~= 0 then
                    -- msg_out[i + j - 1] = msg_out[i + j - 1] ~ ReedSolo.gf_mul(divisor[j], coef)
                    msg_out[i + j - 1] = bitwise_xor(msg_out[i + j - 1], ReedSolo.gf_mul(divisor[j], coef))
                end
            end
        end
    end

    local separator = #msg_out - #divisor + 1
    local quotient = {}
    for i = 1, separator do
        table.insert(quotient, msg_out[i])
    end

    local remainder = {}
    for i = separator + 1, #msg_out do
        table.insert(remainder, msg_out[i])
    end

    return quotient, remainder
end

--- Вычисление синдромов Форни
--- @param synd integer[] -- Синдромы
--- @param pos integer[] -- Позиции ошибок
--- @param nmess integer -- Длина сообщения
--- @return integer[] -- Синдромы Форни
function ReedSolo.rs_forney_syndromes(synd, pos, nmess)
    local erase_pos_reversed = {}
    for _, p in ipairs(pos) do
        table.insert(erase_pos_reversed, nmess - 1 - p)
    end

    local fsynd = {table.unpack(synd, 2)}
    for i = 1, #pos do
        local x = ReedSolo.gf_pow(2, erase_pos_reversed[i])
        for j = 1, #fsynd - 1 do
            -- fsynd[j] = ReedSolo.gf_mul(fsynd[j], x) ~ fsynd[j + 1]
            fsynd[j] = bitwise_xor(ReedSolo.gf_mul(fsynd[j], x), fsynd[j + 1])
        end
    end

    return fsynd
end

--- Нахождение локатора ошибок/искажений с использованием алгоритма Берлекампа-Мэсси
--- @param synd integer[] -- Синдромы
--- @param nsym integer -- Количество символов кода
--- @param erase_loc integer[]|nil -- Полином локатора ошибок
--- @param erase_count integer -- Количество ошибок
--- @return integer[] -- Полином локатора ошибок
function ReedSolo.rs_find_error_locator(synd, nsym, erase_loc, erase_count)
    erase_loc = erase_loc or {1}
    local err_loc = {table.unpack(erase_loc)}
    local old_loc = {table.unpack(erase_loc)}
    erase_count = erase_count or 0

    local synd_shift = 0
    if #synd > nsym then
        synd_shift = #synd - nsym
    end

    for i = 0, nsym - erase_count - 1 do
        local K
        if erase_loc then
            K = erase_count + i + 1 + synd_shift
        else
            K = i + 1 + synd_shift
        end

        local delta = synd[K]
        for j = 1, #err_loc - 1 do
            -- delta = delta ~ ReedSolo.gf_mul(err_loc[#err_loc - j], synd[K - j])
            delta = bitwise_xor(delta, ReedSolo.gf_mul(err_loc[#err_loc - j], synd[K - j]))
        end

        table.insert(old_loc, 0) -- Добавляем 0 в конец old_loc

        if delta ~= 0 then
            if #old_loc > #err_loc then
                local new_loc = ReedSolo.gf_poly_scale(old_loc, delta)
                old_loc = ReedSolo.gf_poly_scale(err_loc, ReedSolo.gf_inverse(delta))
                err_loc = new_loc
            end
            err_loc = ReedSolo.gf_poly_add(err_loc, ReedSolo.gf_poly_scale(old_loc, delta))
        end
    end

    while #err_loc > 0 and err_loc[1] == 0 do
        table.remove(err_loc, 1)
    end

    local errs = #err_loc - 1
    if (errs - erase_count) * 2 + erase_count > nsym then
        error("Too many errors to correct")
    end

    return err_loc
end

--- Нахождение полинома локатора ошибок
--- @param e_pos integer[] -- Позиции ошибок
--- @return integer[] -- Полином локатора ошибок
function ReedSolo.rs_find_errata_locator(e_pos)
    local e_loc = {1}
    for _, i in ipairs(e_pos) do
        e_loc = ReedSolo.gf_poly_mul(e_loc, ReedSolo.gf_poly_add({1}, {ReedSolo.gf_pow(2, i), 0}))
    end
    return e_loc
end

--- Найти позиции ошибок с помощью алгоритма Шиена
--- @param err_loc integer[] -- Полином локатора ошибок
--- @param nmess integer -- Длина исходного сообщения
--- @return integer[] -- Позиции ошибок
function ReedSolo.rs_find_errors(err_loc, nmess)
    local errs = #err_loc - 1
    local err_pos = {}

    for i = 0, nmess - 1 do
        if ReedSolo.gf_poly_eval(err_loc, ReedSolo.gf_pow(2, i)) == 0 then
            table.insert(err_pos, nmess - 1 - i)
        end
    end

    if #err_pos ~= errs then
        error("Too many (or few) errors found using Chien search for the error locator polynomial!")
    end

    return err_pos
end

--- Вычислить оценочный полином ошибок
--- @param synd integer[] -- Синдромы
--- @param err_loc integer[] -- Полином локатора ошибок
--- @param nsym integer -- Количество символов кода
--- @return integer[] -- Полином оценщика ошибок
function ReedSolo.rs_find_error_evaluator(synd, err_loc, nsym)
    -- Создаем делитель вида {1, 0, 0, ..., 0} длиной nsym + 2
    local divisor = {1}
    for i = 1, nsym + 1 do
        table.insert(divisor, 0)
    end

    local product = ReedSolo.gf_poly_mul(synd, err_loc)
    local _, remainder = ReedSolo.gf_poly_div(product, divisor)
    return remainder
end

--- Переворачивает массив
--- @param array table -- Исходный массив
--- @return table -- Перевернутый массив
function ReedSolo.reverse(array)
    local reversed = {}
    for i = #array, 1, -1 do
        table.insert(reversed, array[i])
    end
    return reversed
end

--- Исправление ошибок методом Форни
--- @param msg_in integer[] -- Входное сообщение
--- @param synd integer[] -- Синдромы
--- @param err_pos integer[] -- Позиции ошибок
--- @return integer[] -- Исправленное сообщение
function ReedSolo.rs_correct_errata(msg_in, synd, err_pos)
    local coef_pos = {}
    for _, p in ipairs(err_pos) do
        table.insert(coef_pos, #msg_in - 1 - p)
    end

    local err_loc = ReedSolo.rs_find_errata_locator(coef_pos)
    local err_eval = ReedSolo.rs_find_error_evaluator(ReedSolo.reverse(synd), err_loc, #err_loc - 1)
    err_eval = ReedSolo.reverse(err_eval)

    local X = {}
    for _, pos in ipairs(coef_pos) do
        local l = 255 - pos
        table.insert(X, ReedSolo.gf_pow(2, -l))
    end

    local E = {}
    for i = 1, #msg_in do
        E[i] = 0
    end

    for i, Xi in ipairs(X) do
        local Xi_inv = ReedSolo.gf_inverse(Xi)
        local err_loc_prime_tmp = {}

        for j, Xj in ipairs(X) do
            if j ~= i then
                table.insert(err_loc_prime_tmp, ReedSolo.gf_sub(1, ReedSolo.gf_mul(Xi_inv, Xj)))
            end
        end

        local err_loc_prime = 1
        for _, coef in ipairs(err_loc_prime_tmp) do
            err_loc_prime = ReedSolo.gf_mul(err_loc_prime, coef)
        end

        local y = ReedSolo.gf_poly_eval(ReedSolo.reverse(err_eval), Xi_inv)
        y = ReedSolo.gf_mul(ReedSolo.gf_pow(Xi, 1), y)

        local magnitude = ReedSolo.gf_div(y, err_loc_prime)
        E[err_pos[i] + 1] = magnitude -- Lua uses 1-based indexing
    end

    return ReedSolo.gf_poly_add(msg_in, E)
end

--- Основная функция декодирования Рида-Соломона
--- @param msg_in integer[] -- Входное сообщение
--- @param nsym integer -- Количество символов для исправления
--- @param erase_pos integer[] -- Позиции стирания
--- @return integer[], integer[] -- Декодированное сообщение и исправляющий код
function ReedSolo.rs_correct_msg(msg_in, nsym, erase_pos)
    erase_pos = erase_pos or {}
    local msg_out = {table.unpack(msg_in)}

    for _, e_pos in ipairs(erase_pos) do
        msg_out[e_pos] = 0
    end

    if #erase_pos > nsym then
        error("Too many erasures to correct")
    end

    local synd = ReedSolo.rs_calc_syndromes(msg_out, nsym)
    if math.max(table.unpack(synd)) == 0 then
        return {table.unpack(msg_out, 1, #msg_out - nsym)}, {table.unpack(msg_out, #msg_out - nsym + 1)}
    end

    local fsynd = ReedSolo.rs_forney_syndromes(synd, erase_pos, #msg_out)
    local err_loc = ReedSolo.rs_find_error_locator(fsynd, nsym, #erase_pos)
    local err_pos = ReedSolo.rs_find_errors(err_loc, #msg_out)

    if not err_pos then
        error("Could not locate error")
    end

    msg_out = ReedSolo.rs_correct_errata(msg_out, synd, {table.unpack(erase_pos, err_pos)})
    synd = ReedSolo.rs_calc_syndromes(msg_out, nsym)

    if math.max(table.unpack(synd)) > 0 then
        error("Could not correct message")
    end

    return table.unpack(msg_out, 1, #msg_out - nsym), table.unpack(msg_out, #msg_out - nsym + 1)
end

return ReedSolo
