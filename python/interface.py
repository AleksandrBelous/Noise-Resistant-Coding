from tkinter import Canvas, StringVar, Tk, filedialog

# Импортируем функции из модулей hamming.py и interface_utils.py
from hamming import *
from interface_utils import *
from block_parity import *
from reedSolo import *


# Создаем класс Window, который наследуется от класса Tk
class Window(Tk):

    # Метод __init__ будет вызван при создании экземпляра класса Window
    def __init__(self):

        # Вызываем конструктор родительского класса
        super().__init__()

        # Задаем заголовок окна
        self.title("Три метода")

        # Запрещаем изменять размеры окна
        self.resizable(False, False)

        # Помещаем окно по центру экрана
        self.eval("tk::PlaceWindow . center")

        # Создаем холст размером 400x300 с рамкой relief='raised'
        self.canvas = Canvas(
            self, width=400, height=400, relief="raised", background="gray"
        )

        # Размещаем холст на окне
        self.canvas.pack()

        # Создаем переменную типа StringVar для ввода данных
        self.input_text = StringVar()
        self.output_text = StringVar()

        # Добавляем callback-функцию self.button_state_controller для отслеживания изменений в self.input_text
        self.input_text.trace("w", self.button_state_controller)
        self.output_text.trace("w", self.button_state_controller)

        # Создаем переменные типа StringVar для вывода сообщений
        self.label_text = StringVar()

        # Создаем несколько переменных для шрифтов
        title_font = ("Bahnschrift", 16, "bold", "underline")
        text_font = (
            "Bahnschrift",
            14,
        )
        button_font = ("bahnschrift", 12, "bold")

        # Создаем объект функции validate_input, используя метод register класса Tk,
        # чтобы проверять корректность введенных данных в поле ввода
        validate_command = (self.register(self.validate_input), "%P")

        # Создаем заголовок 'Triple Coding' на холсте
        create_label(self.canvas, "Три кодирования", title_font, 200, 25)

        # Создаём заголовок 'Choose code method:'
        create_label(self.canvas, "Выберите метод кодирования:", text_font, 200, 60)

        # Создаём переменную типа IntVar() для хранения значения выбранного значения
        self.var = IntVar()

        # Создаем radio button для выбора типа информации
        self.radio_button = create_radio_buttons(
            self.canvas,
            self.var,
            ("Открытая информация", "Закрытая информация"),
            text_font,
            200,
            100,
        )

        # Создаем текстовую метку 'Enter the data bits:' на холсте
        create_label(self.canvas, "Выберете данные: ", text_font, 200, 190)
        # # Создаем поле ввода на холсте
        self.entry_input = create_entry(
            self.canvas, self.input_text, text_font, 120, 230, validate_command
        )

        # Создаем кнопку 'Открыть файл', вызывая соответствующую функцию при нажатии
        self.open_button = create_button(
            self.canvas, "Открыть файл", self.open_txt, button_font, 300, 230
        )
        self.open_button.config(state="normal")

        # Создаем кнопки 'Encode' и 'Decode' на холсте, вызывая соответствующие функции при нажатии
        self.button_encode = create_button(
            self.canvas, "Encode", self.get_code, button_font, 160, 270
        )
        self.button_decode = create_button(
            self.canvas, "Decode", self.get_decode, button_font, 240, 270
        )

        # Создаем метку для вывода результата на холсте
        create_label(self.canvas, self.label_text, text_font, 200, 310)

        # Создаем поле вывода на холсте
        self.entry_output = create_entry(
            self.canvas, self.output_text, text_font, 120, 350
        )
        # Создаем кнопку 'Сохранить в файл', вызывая соответствующую функцию при нажатии
        self.save_button = create_button(
            self.canvas, "Сохранить в файл", self.save_txt, button_font, 300, 350
        )

    # функция открытия текстового файла через диалоговое окно
    def open_txt(self):
        text_file = filedialog.askopenfilename(
            title="Открыть файл", filetypes=(("Text Files", "*.txt"),)
        )
        text_file = open(text_file, "r+", encoding="utf-8")
        stuff = text_file.read()
        self.input_text.set(stuff)
        text_file.close()

    # функция сохранения текстового файла через диалоговое окно
    def save_txt(self):

        text_file = filedialog.asksaveasfile(
            title="Сохранить файл",
            filetypes=(("Text Files", "*.txt"),),
            defaultextension=".txt",
        )
        text_file.write(str(self.output_text.get()))

    # Функция для декодирования бинарной строки в текст
    def decode_binary_string(self, s):
        return "".join(
            chr(int(s[i * 11 : i * 11 + 11], 2)) for i in range(len(s) // 11)
        )

    def get_code(self):
        # Устанавливаем текст надписи "Generated data: "
        self.label_text.set("Зашифрованные данные: ")
        # Вызываем метод get_answer с параметром True
        self.get_answer(True)

    def get_decode(self):
        # Устанавливаем текст надписи "Decoded data: "
        self.label_text.set("Дешифрованные данные: ")
        # Вызываем метод get_answer с параметром False
        self.get_answer(False)

    def get_answer(self, encode=True):
        if encode:
            # Устанавливаем праметры для кодирования
            params = 0b00
            # Получаем биты из поля ввода и преобразуем их в битовую строку
            bits = self.entry_input.get()
            # Устанавливаем параметр в зависимости от длины, меняем старший бит
            if len(bits) > 1000:
                params += 2

            bits = "".join("{:011b}".format(ord(c)) for c in bits)
            # Устанавливаем параметр в зависимости закрытой/открытой информации, меняем младший бит
            if self.var.get() == 2:
                params += 1

            # Переход в случай метода Хэмминга
            if params == 0b00:
                # Преобразуем битовую строку в список целых чисел
                bits = [int(bit) for bit in bits]
                # Получаем закодированные данные
                print(f"hamming_code bits: {bits}")
                result = hamming_code(bits)
                print(f"hamming_code result: {result}")
                # Преобразуем список целых чисел в строку битов и устанавливаем в поле вывода
                result = "".join(str(bit) for bit in result)
                self.output_text.set("00" + result)
            # Переход в случай метода Рида-Соломона
            elif params == 0b11:
                # Преобразуем битовую строку в список целых чисел
                bits = [int(bit) for bit in bits]
                result = rs_encode_msg(bits, 9)
                # Преобразуем список целых чисел в строку битов и устанавливаем в поле вывода
                result = "".join(str(bit) for bit in result)
                # self.output_text.set(bin(params)[2:] + result)
                self.output_text.set("11" + result)
            # Переход в случай метода блочного с проверкой чётности
            elif params == 0b10 or params == 0b01:
                result = block_encode(bits)
                self.output_text.set("01" + result)

        else:
            # Получаем биты из поля ввода и преобразуем в список целых чисел
            params = int(self.entry_input.get()[:2], 2)
            print(f"in get_answer: params={params}")
            bits = self.entry_input.get()[2:]
            print(f"in get_answer: bits={bits}")
            if params == 0b00:
                bits = [int(bit) for bit in bits]
                # Получаем раскодированные данные
                result = hamming_decode(bits)
                # Преобразуем список целых чисел в строку битов и расшифровываем ее
                result = "".join(str(bit) for bit in result)
                result = self.decode_binary_string(result)
                self.output_text.set(result)
            elif params == 0b11:
                bits = [int(bit) for bit in bits]
                print(f"in get_answer: params == 0b11 bits={bits}")
                corrected_message, corrected_ecc = rs_correct_msg(bits, 9)
                # Преобразуем список целых чисел в строку битов и расшифровываем ее
                result = "".join(str(bit) for bit in corrected_message)
                result = self.decode_binary_string(result)
                self.output_text.set(result)
            elif params == 0b10 or params == 0b01:
                result = block_decode(bits)
                result = self.decode_binary_string(result)
                # Устанавливаем расшифрованные данные в поле вывода
                self.output_text.set(result)

    @staticmethod
    def validate_input(value):
        if len(value) != 0:
            # Если введенный символ не является пустым, то оставляем его
            value = value[-1]
        return True

    def button_state_controller(self, *_):
        if len(self.input_text.get()) > 0:
            # Если в поле ввода есть данные, то разблокируем кнопки
            self.button_encode.config(state="normal")
            self.button_decode.config(state="normal")
        else:
            # Если поле ввода пусто, то блокируем кнопки
            self.button_encode.config(state="disabled")
            self.button_decode.config(state="disabled")

        if len(self.entry_output.get()) > 0:
            # Если в поле вывода есть данные, то разблокируем сохранение
            self.save_button.config(state="normal")
        else:
            # Если поле вывода пусто, то блокируем сохранение
            self.save_button.config(state="disabled")
