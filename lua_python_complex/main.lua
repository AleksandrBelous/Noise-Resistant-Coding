-- Получаем путь к текущему Lua-скрипту (main.lua)
local current_dir = string.match(debug.getinfo(1, "S").source, "^@(.*/)")
print("Current directory:", current_dir)

local python_code = [[
# from interface import *

import os
import re
import textwrap

# Путь к Lua-файлу с кодом
current_dir = "]] .. current_dir .. [["
interface_lua_code_file = os.path.join(current_dir, "interface.lua")

with open(interface_lua_code_file, "r") as file:
    lua_content = file.read()

# Регулярное выражение для поиска кода
match = re.search(r"\[=\[(.*?)\]=\]", lua_content, re.DOTALL)
if match:
    python_code = match.group(1)  # Извлекаем содержимое блока [=[ ... ]=]

    # Удаляем лишние отступы
    python_code = textwrap.dedent(python_code)

    # Выполняем код
    exec(python_code)

    # Теперь можно использовать функции из interface
    Window().mainloop()
else:
    raise ValueError("Code block not found in Lua file")
]]

-- Создаем временный файл в той же папке, что и main.lua
local temp_file = current_dir .. "temp_code.py"
local file = io.open(temp_file, "w")
file:write(python_code)
file:close()

-- Выполняем код через файл
os.execute("python " .. temp_file)

-- Удаляем временный файл
os.remove(temp_file)
