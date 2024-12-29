local interface_utils_code = [[
from tkinter import Button, Entry, Label, Radiobutton, IntVar


def create_label(canvas, text, custom_font, x, y):
    # Создание метки с текстом text и шрифтом custom_font
    # Если тип текста строка, создается объект Label со свойством text, иначе со свойством textvariable
    # Создание элемента на холсте canvas с координатами (x, y)
    # Возвращается созданный элемент
    if isinstance(text, str):
        label = Label(text=text, font=custom_font)
    else:
        label = Label(textvariable=text, font=custom_font, background="gray")
    canvas.create_window(x, y, window=label)
    return label


def create_button(canvas, text, command, custom_font, x, y):
    # Создание кнопки с текстом text, командой command, и шрифтом custom_font
    # Установка начального состояния кнопки в 'disabled'
    # Создание элемента на холсте canvas с координатами (x, y)
    # Возвращается созданный элемент
    button = Button(
        text=text,
        state="disabled",
        command=command,
        font=custom_font,
        background="gray",
    )
    canvas.create_window(x, y, window=button)
    return button


def create_entry(canvas, text_variable, custom_font, x, y, validate_command=None):
    # Создание поля ввода с текстовой переменной text_variable и шрифтом custom_font
    # Если задана команда validate_command, поля ввода валидируется с помощью 'validatecommand'
    # В противном случае, поле ввода устанавливается в состояние 'readonly'
    # Создание элемента на холсте canvas с координатами (x, y)
    # Возвращается созданный элемент
    if validate_command is not None:
        entry = Entry(
            textvariable=text_variable,
            validate="all",
            validatecommand=validate_command,
            font=custom_font,
        )
    else:
        entry = Entry(textvariable=text_variable, state="readonly", font=custom_font)
    canvas.create_window(x, y, window=entry)
    return entry


def create_radio_buttons(canvas, var, options, custom_font, x, y):
    # Создание переменной для хранения выбранного значения
    var.set(1)  # Устанавливаем начальное значение по умолчанию

    # Создание радио-кнопок для каждой опции
    for i, option in enumerate(options):
        radio_button = Radiobutton(
            canvas, text=option, variable=var, value=i + 1, font=custom_font
        )
        canvas.create_window(x, y + (i * 25), window=radio_button)
    # Возвращаем переменную с выбранным значением
    return radio_button

]]

return interface_utils_code
