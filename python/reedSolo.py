# Создаем списки для логарифмических значений элементов поля Галуа
# `gf_exp` хранит значения элементов поля Галуа в экспоненциальном представлении,
# `gf_log` хранит логарифмические значения этих элементов
gf_exp = [0] * 512
gf_log = [0] * 256


# Операция умножения двух элементов поля Галуа
def gf_mul(x, y):
    print(f"in gf_mul, x={x}, y={y}")
    # Если один из множителей равен 0, то результат равен 0
    if x == 0 or y == 0:
        return 0
    print(f"gf_log[x]={gf_log[x]}")
    print(f"gf_log[y]={gf_log[y]}")
    # Используем свойства поля Галуа для вычисления произведения
    return gf_exp[gf_log[x] + gf_log[y]]


# Умножение многочленов в поле Галуа
def gf_poly_mul(p, q):
    # Результирующий многочлен имеет степень, равную сумме степеней исходных многочленов
    r = [0] * (len(p) + len(q) - 1)
    for j in range(0, len(q)):
        # print(f"j={j}")
        for i in range(0, len(p)):
            # print(f"i={i}")
            # Коэффициент результирующего многочлена на i+j-м месте вычисляется как XOR произведения коэффициентов p[i] и q[j]
            # с использованием операции умножения элементов поля Галуа
            # print(f"p[i]={p[i]}, q[j]={q[j]}")
            r[i + j] ^= gf_mul(p[i], q[j])
    return r


# Генерация порождающего многочлена кода Рида-Соломона
def rs_generator_poly(nsym):
    g = [1]
    for i in range(0, nsym):
        # print(f"i={i}, g={g}----------")
        # Коэффициенты порождающего многочлена вычисляются как произведение (x-α^i), где α - первообразный элемент поля Галуа
        # Используем функцию `gf_poly_mul` для вычисления произведения многочленов
        g = gf_poly_mul(g, [1, gf_exp[i]])
        # print(f"i={i}, g={g}----------")
    return g


def rs_encode_msg(msg_in, nsym):
    # Основная функция кодирования Рида-Соломона,
    # использующая полиномиальное деление (алгоритм расширенного
    # синтетического деления)

    # Проверяем, что сообщение не слишком длинное
    # if (len(msg_in) + nsym) > 255:
    #     raise ValueError("Message is too long (%i when max is 255)" % (len(msg_in) + nsym))

    # Получаем генераторный полином для Рида-Соломона
    gen = rs_generator_poly(nsym)

    # Инициализировать msg_out со значением msg_in и добавить к нему суффиксные байты, дополненные 0.
    msg_out = [0] * (len(msg_in) + len(gen) - 1)
    msg_out[: len(msg_in)] = msg_in

    # Synthetic division main loop
    for i in range(len(msg_in)):
        coef = msg_out[i]

        if coef != 0:  # Избегайте ошибок в журнале (0)
            for j in range(1, len(gen)):
                # Поскольку первая цифра многочлена равна 1, (1 ^ 1 == 0), вы можете пропустить
                msg_out[i + j] ^= gf_mul(gen[j], coef)

    # После деления msg_out содержит частное msg_out [: len (msg_in)] и остаток msg_out [len (msg_in):].
    # Код RS использует только остаток, поэтому мы используем исходную информацию, чтобы покрыть частное, чтобы получить полный код.
    msg_out[: len(msg_in)] = msg_in

    return msg_out


def gf_pow(x, power):
    # Функция, которая реализует операцию возведения в степень для конечного поля Галуа GF(2^8)
    return gf_exp[(gf_log[x] * power) % 255]


def gf_inverse(x):
    # Функция, которая реализует операцию нахождения обратного элемента для конечного поля Галуа GF(2^8)
    return gf_exp[255 - gf_log[x]]  # gf_inverse(x) == gf_div(1, x)


def gf_sub(x, y):
    # Вычитание двух чисел в поле Галуа GF(2^8)
    return x ^ y


def gf_poly_add(p, q):
    # Сложение двух многочленов в поле Галуа GF(2^8)
    r = [0] * max(len(p), len(q))
    for i in range(0, len(p)):
        r[i + len(r) - len(p)] = p[i]
    for i in range(0, len(q)):
        r[i + len(r) - len(q)] ^= q[i]
    return r


def gf_poly_eval(p, x):
    # Вычисление значения многочлена p в точке x в поле Галуа GF(2^8)
    y = p[0]
    for i in range(1, len(p)):
        y = gf_mul(y, x) ^ p[i]
    return y


def rs_calc_syndromes(msg, nsym):
    # вычисляет синдромы для заданного сообщения в соответствии с алгоритмом
    print(f"in rs_calc_syndromes, msg={msg}, nsym={nsym}")
    synd = [0] * nsym
    for i in range(0, nsym):
        synd[i] = gf_poly_eval(msg, gf_pow(2, i))
    return [0] + synd


def gf_poly_scale(p, x):
    # Умножение многочлена на константу в поле Галуа GF(2^8)
    print(f"in gf_poly_scale, p={p}, x={x}")
    r = [0] * len(p)
    for i in range(0, len(p)):
        r[i] = gf_mul(p[i], x)
    return r


def gf_div(x, y):
    # Деление двух чисел в поле Галуа GF(2^8)
    if y == 0:
        raise ZeroDivisionError()
    if x == 0:
        return 0
    return gf_exp[(gf_log[x] + 255 - gf_log[y]) % 255]


def gf_poly_div(dividend, divisor):
    """Быстрое полиномиальное деление, подходящее для области GF (2 ^ p)."""
    # Примечание: полиномиальные коэффициенты нужно сортировать от высокого к низкому значению,
    # например: 1 + 2x + 5x ^ 2 = [5, 2, 1], а не [1, 2, 5]

    msg_out = list(
        dividend
    )  # Скопировать дивиденд (байты ecc хвостового суффикса, дополненные 0)

    # Выполнение быстрого полиномиального деления
    for i in range(0, len(dividend) - (len(divisor) - 1)):
        # msg_out[i] /= normalizer
        coef = msg_out[i]
        if coef != 0:  # Избегайте ошибок в журнале (0).
            for j in range(1, len(divisor)):
                if divisor[j] != 0:  # log(0) is undefined
                    msg_out[i + j] ^= gf_mul(
                        divisor[j], coef
                    )  # msg_out [i + j] + = -divisor [j] * coef
                    # (эквивалентно математическому выражению, но операция XOR эффективна)

    # msg_out содержит частное и остаток.Наибольшая степень остатка (== length-1) совпадает с делителем,
    # и точка останова вычисляется ниже.
    separator = -(len(divisor) - 1)
    return msg_out[:separator], msg_out[separator:]  # Вернуть частное, остаток.


def rs_forney_syndromes(synd, pos, nmess):
    # Функция для вычисления синдромов Форни.
    # Синдромы Форни - это модифицированные синдромы, которые вычисляются для вычисления только ошибок,
    # при этом стирания игнорируются.
    # Не путайте синдромы Форни и алгоритм Форни, который используется для коррекции информации
    # на основе расположения ошибок.

    # Подготовить позиции в коэффициентной форме (вместо позиций стирания)
    erase_pos_reversed = [nmess - 1 - p for p in pos]

    # Оптимизированный метод, все операции инлайновые
    fsynd = list(
        synd[1:]
    )  # создаем копию и удаляем первый коэффициент, который всегда равен 0 по определению
    for i in range(0, len(pos)):
        x = gf_pow(
            2, erase_pos_reversed[i]
        )  # вычисляем степень x в соответствии с текущей позицией стирания
        for j in range(0, len(fsynd) - 1):
            fsynd[j] = gf_mul(fsynd[j], x) ^ fsynd[j + 1]  # вычисляем новый коэффициент

    return fsynd


def rs_find_error_locator(synd, nsym, erase_loc=None, erase_count=0):
    """Find error/errata locator and evaluator polynomials with Berlekamp-Massey algorithm"""
    # Использование алгоритма BM для итеративного вычисления полинома локатора ошибок.
    # Вычисление разностного элемента Delta для определения необходимости обновления полинома локатора ошибок.

    # Init the polynomials
    if erase_loc:
        err_loc = list(erase_loc)
        old_loc = list(erase_loc)
    else:
        err_loc = [1]  # Sigma(errors/errata locator polynomial) .
        old_loc = [
            1
        ]  # BM - итерационный алгоритм, который должен сравнивать старые и новые значения (Sigma),
        # чтобы определить, какие переменные необходимо обновить.

    synd_shift = 0
    if len(synd) > nsym:
        synd_shift = len(synd) - nsym

    for i in range(0, nsym - erase_count):
        # если для инициализации полинома errors locator был предоставлен полином errors locator,
        # то мы должны пропустить первые итерации erase_count
        if erase_loc:
            K = erase_count + i + synd_shift
        # Если erasures locator не предусмотрен, то либо стирания не учитываются, либо мы используем синдромы Форни,
        # поэтому нам не нужно использовать ни erase_count, ни erase_loc.
        else:
            K = i + synd_shift

        # Вычисляем дельту расхождения
        # Рассчитать дельту: локатор ошибок и синдромы выполняют полиномиальное умножение.
        # delta = gf_poly_mul (err_loc [:: - 1], synd) [K] # Строго говоря, это должен быть
        # gf_poly_add (synd [:: - 1], [1]) [:: - 1], но для правильного декодирования Это не обязательно.
        # И это также оптимизирует эффективность: мы вычисляем только полиномиальное умножение слагаемого К.
        # Избегаем вложенных циклов.
        delta = synd[K]
        for j in range(1, len(err_loc)):
            delta ^= gf_mul(err_loc[-(j + 1)], synd[K - j])
        # print("delta", K, delta, list(gf_poly_mul(err_loc[::-1], synd))) # debugline

        old_loc = old_loc + [0]

        # Расчет ошибочных локатора и полинома оценщика
        if delta != 0:  # дельта не обновляется, пока не станет 0
            if len(old_loc) > len(err_loc):
                # Вычислить сигму (ошибочный локатор полинома)
                new_loc = gf_poly_scale(old_loc, delta)
                old_loc = gf_poly_scale(err_loc, gf_inverse(delta))
                err_loc = new_loc

            # Обновление Delta
            err_loc = gf_poly_add(err_loc, gf_poly_scale(old_loc, delta))

    # Проверьте правильность результата или слишком много ошибок, которые нужно исправить
    while len(err_loc) and err_loc[0] == 0:
        del err_loc[0]  # Исключить первые 0
    errs = len(err_loc) - 1
    if (errs - erase_count) * 2 + erase_count > nsym:
        raise Exception("Too many errors to correct")  # Слишком много ошибок

    return err_loc


def rs_find_errata_locator(e_pos):
    # Инициализируем e_loc = [1] вместо [0] для вычисления умножения
    e_loc = [1]
    # Вычисляем множитель erasures_loc = product(1 - x*alpha**i) для каждой позиции i в e_pos
    # Здесь alpha - выбранный множитель для вычисления полиномов, который используется в gf_poly_eval и gf_poly_mul
    for i in e_pos:
        e_loc = gf_poly_mul(e_loc, gf_poly_add([1], [gf_pow(2, i), 0]))
    return e_loc


def rs_find_errors(err_loc, nmess):  # nmess - длина исходного сообщения msg_in
    """Находим корни (т.е. места, где ошибка равна нулю) полинома ошибок путем перебора значений, это своего рода поиск Шиена
    (но менее эффективный, поиск Шиена - это способ вычисления полинома так, что каждое вычисление занимает постоянное время).
    """
    errs = len(err_loc) - 1
    err_pos = []
    print(f"err_loc = {err_loc}, nmess = {nmess}")
    # Обычно мы должны бы проверить все 2^8 возможных значений,
    # но здесь мы оптимизировали алгоритм и проверяем только "интересные" символы
    for i in range(nmess):
        # Это значение равно 0? Значит, это корень полинома ошибок,
        # другими словами, это место ошибки
        if gf_poly_eval(err_loc, gf_pow(2, i)) == 0:
            err_pos.append(nmess - 1 - i)
    # Проверяем, что количество найденных ошибок/исправлений совпадает с длиной полинома локатора ошибок
    if len(err_pos) != errs:
        # Не удалось найти позиции ошибок
        raise Exception(
            "Слишком много (или мало) ошибок, найденных методом поиска Шиена для локатора ошибок!"
        )
    return err_pos


def rs_find_error_evaluator(synd, err_loc, nsym):
    """Compute the error (or erasures if you supply sigma=erasures locator polynomial, or errata) evaluator polynomial Omega
    from the syndrome and the error/erasures/errata locator Sigma."""

    """Вычисление ошибку (или стирания, если sigma=erasures locator polynomial или ошибки) evaluator polynomial Omega
    из синдрома и локатора ошибок / стираний / опечаток """

    # Omega(x) = [ Synd(x) * Error_loc(x) ] mod x^(n-k+1)
    _, remainder = gf_poly_div(
        gf_poly_mul(synd, err_loc), ([1] + [0] * (nsym + 1))
    )  # деление полиномов, чтобы усечь полином до n - k + 1

    return remainder


def rs_correct_errata(
    msg_in, synd, err_pos
):  # err_pos is a list of the positions of the errors/erasures/errata
    """Алгоритм Forney вычисляет значения (величину ошибки) для исправления входного сообщения ."""
    # Объединить предыдущие результаты позиционирования для распознавания ошибок (ошибочный локатор полинома)
    # Преобразовать положение в полиномиальный коэффициент
    # (например: преобразовать из [0, 1, 2] в [len (msg) -1, len (msg) -2, len (msg) -3])
    coef_pos = [len(msg_in) - 1 - p for p in err_pos]
    err_loc = rs_find_errata_locator(coef_pos)
    # Расчет полинома оценщика ошибок (термин называется Омега или Гамма)
    err_eval = rs_find_error_evaluator(synd[::-1], err_loc, len(err_loc) - 1)[::-1]
    print(f"\n\n\nerr_eval = {err_eval}\n\n\n")

    # Алгоритм Chien ищет err_pos, чтобы получить позицию ошибки X
    # (корни многочлена локатора ошибок, т. Е. Где он оценивается в 0)
    X = []
    for i in range(0, len(coef_pos)):
        l = 255 - coef_pos[i]
        X.append(gf_pow(2, -l))

    # Forney algorithm: compute the magnitudes
    E = [0] * (len(msg_in))
    Xlength = len(X)
    for i, Xi in enumerate(X):

        Xi_inv = gf_inverse(Xi)

        # Используя формальную производную локатора ошибок в качестве знаменателя алгоритма Форни,
        # i-е значение ошибки: error_evaluator (gf_inverse (Xi)) / error_locator_derivative (gf_inverse (Xi)).
        err_loc_prime_tmp = []
        for j in range(0, Xlength):
            if j != i:
                err_loc_prime_tmp.append(gf_sub(1, gf_mul(Xi_inv, X[j])))
        # Следующее умножение вычисляет знаменатель, требуемый алгоритмом Форни (производная локатора ошибок)
        err_loc_prime = 1
        for coef in err_loc_prime_tmp:
            err_loc_prime = gf_mul(err_loc_prime, coef)
        # Эквивалентно: err_loc_prime = functools.reduce (gf_mul, err_loc_prime_tmp, 1)

        # Compute y (evaluation of the errata evaluator polynomial)
        # Более простая реализация алгоритма Форни:
        # Yl = omega(Xl.inverse()) / prod(1 - Xj*Xl.inverse()) for j in len(X)
        y = gf_poly_eval(err_eval[::-1], Xi_inv)  # Числитель алгоритма Форни
        y = gf_mul(gf_pow(Xi, 1), y)

        # Compute the magnitude
        magnitude = gf_div(
            y, err_loc_prime
        )  # magnitude value of the error, calculated by the Forney algorithm
        E[err_pos[i]] = (
            magnitude  # store the magnitude for this error into the magnitude polynomial
        )

    msg_in = gf_poly_add(msg_in, E)
    return msg_in


def rs_correct_msg(msg_in, nsym, erase_pos=None):
    """Основная функция декодирования Рида-Соломона"""
    # if len(msg_in) > 255:  # нельзя расшифровать, сообщение слишком большое
    #     raise ValueError("Message is too long (%i when max is 255)" % len(msg_in))
    print("in rs_correct_msg")

    msg_out = list(msg_in)  # копия сообщения
    # стирает: для удобства отладки для декодирования установите в нуль (необязательно)
    if erase_pos is None:
        erase_pos = []
    else:
        for e_pos in erase_pos:
            msg_out[e_pos] = 0
    # проверяет, не слишком ли много мер для исправления (за пределами одноэлементной границы)
    if len(erase_pos) > nsym:
        print(f"erase_pos={erase_pos}, len={len(erase_pos)} > {nsym}, nsym={nsym}")
        raise Exception("Too many erasures to correct")
    # prepare the syndrome polynomial using only errors.
    synd = rs_calc_syndromes(msg_out, nsym)
    # Проверrf, есть ли ошибка в кодовом слове. Если ошибки нет (все коэффициенты синдрома равны 0),
    # кодовое слово возвращается как есть.
    if max(synd) == 0:
        return msg_out[:-nsym], msg_out[-nsym:]  # no errors

    # вычисляет синдромы Форни, которые скрывают удаления из исходного синдрома
    # (так что BM придется иметь дело только с ошибками, а не со стираниями)
    fsynd = rs_forney_syndromes(synd, erase_pos, len(msg_out))
    # вычисляет полином локатора ошибок с использованием Берлекэмпа-Мэсси
    err_loc = rs_find_error_locator(fsynd, nsym, erase_count=len(erase_pos))
    # находит ошибки в сообщениях с помощью поиска Chien (или поиска методом перебора)
    err_pos = rs_find_errors(err_loc[::-1], len(msg_out))
    if err_pos is None:
        raise Exception("Could not locate error")  # ошибка определения местоположения

    # Yаходит значения ошибок и применяет их для исправления сообщения
    # вычисляет errata evaluator и errata magnitude polynomials, а затем исправляет ошибки и erasures
    msg_out = rs_correct_errata(msg_out, synd, (erase_pos + err_pos))
    # (поскольку мы исправим как ошибки, так и erasures, поэтому нам нужен полный текст)
    # проверяет, полностью ли восстановлено окончательное сообщение
    synd = rs_calc_syndromes(msg_out, nsym)
    if max(synd) > 0:
        raise Exception(
            "Could not correct message"
        )  # сообщение не удалось восстановить
    # возвращает успешно декодированное сообщение
    return msg_out[:-nsym], msg_out[-nsym:]
