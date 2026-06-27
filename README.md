# Time Calculator (Калькулятор Времени)

Удобное приложение на Python с графическим интерфейсом для вычисления разницы во времени, сложения и вычитания часов и минут. Интерфейс построен на `customtkinter`, приложение умеет сворачиваться в системный трей.

## Особенности
- Современный и минималистичный интерфейс (CustomTkinter)
- Подсчет разницы между двумя отметками времени
- Сворачивание в системный трей (`pystray`)
- Темная/светлая тема (синхронизируется с системой)

## Как использовать
1. Зайти в [Releases](../../releases)
2. Скачать `TimeCalculator.exe`

## Разработка и поддержка проекта
Если вы хотите модифицировать код или собрать `exe` файл самостоятельно из исходников, выполните следующие шаги:

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/WesternEugene/time-calculator.git
   cd time-calculator
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Запуск исходного кода:
   ```bash
   python main.py
   ```

4. Сборка EXE-файла (требуется `pyinstaller`):
   ```bash
   pip install pyinstaller
   python -m PyInstaller --noconsole --onefile --icon=icon.ico --add-data "icon.ico;." --name TimeCalculator main.py
   ```

## Зависимости
- `customtkinter`
- `pystray`
- `Pillow`
