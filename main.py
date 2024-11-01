import tkinter as tk
from tkinter import ttk
import requests

target_code = ''
currency_dict = {}  # Словарь для сопоставления ID и имени криптовалюты


def generate_currency_list():
    '''Функция для генерации списка названий криптовалют'''
    currency_names = []  # Инициализация пустого списка для хранения ID криптовалют
    # URL для получения списка криптовалют
    url = "https://api.coingecko.com/api/v3/coins/list"
    headers = {"accept": "application/json"}  # Заголовки для запроса
    try:
        # Выполнение HTTP-запроса
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на успешность запроса
        data = response.json()  # Преобразование ответа в JSON-формат
        for coin in data:
            currency_names.append(coin['id'])  # Извлечение ID криптовалюты
            # Сохранение имени криптовалюты в словаре
            currency_dict[coin['id']] = coin['name']
    except requests.RequestException as e:
        print(f"Ошибка при получении списка криптовалют: {e}")
    return currency_names  # Возврат списка ID криптовалют


def get_exchange_rate():
    '''Функция для получения курса обмена криптовалюты'''
    global target_code
    # Получение выбранной криптовалюты и преобразование в нижний регистр
    target_code = combobox_currency.get().lower()
    if not target_code:
        label_entry.config(text='Неверное название валюты', font=(
            'Arial', 12), fg='red')  # Сообщение об ошибке, если поле пустое
        return

    # Обновление метки с полным названием криптовалюты
    if target_code in currency_dict:
        label_name.config(text=f'Выбранная криптовалюта: {
                          currency_dict[target_code]}', font=('Arial', 12), fg='black')
    else:
        label_name.config(text='Криптовалюта не найдена',
                          font=('Arial', 12), fg='red')
        return

    # URL для получения курса обмена
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={
        target_code}&vs_currencies=usd"
    headers = {"accept": "application/json"}  # Заголовки для запроса
    try:
        # Выполнение HTTP-запроса
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на успешность запроса
        data = response.json()  # Преобразование ответа в JSON-формат
        if target_code in data:
            exchange_rate = data[target_code]['usd']  # Извлечение курса обмена
            label_entry.config(text=f'Курс обмена {target_code.upper()} к USD: {
                               exchange_rate}', font=('Arial', 12), fg='black')  # Обновление метки с результатом
        else:
            label_entry.config(text='Отсутствуют данные торгов', font=(
                'Arial', 12), fg='red')  # Сообщение об ошибке, если криптовалюта не найдена
    except requests.RequestException as e:
        # Сообщение об ошибке в случае проблем с запросом
        label_entry.config(text=f'Ошибка: {e}', font=('Arial', 12), fg='red')
    except KeyError as ex:
        label_entry.config(text=f'Ошибка: Эта криптовалюта не торгуется через {
                           ex}', font=('Arial', 12), fg='red')


# Создание главного окна приложения
root = tk.Tk()
root.title('Курсы обмена криптовалют')  # Установка заголовка окна
root.geometry('500x250')  # Установка размеров окна

# Генерация списка названий криптовалют
currency_list = generate_currency_list()

# Создание метки для инструкции
label_currency = tk.Label(root, text='Введите название криптовалюты:')
label_currency.pack(pady=[10, 10])  # Размещение метки в окне с отступами

# Создание выпадающего списка для выбора криптовалюты
combobox_currency = ttk.Combobox(
    root, values=currency_list, height=30, width=30)
# Размещение выпадающего списка в окне с отступами
combobox_currency.pack(pady=[10, 10])

# Установка значения по умолчанию в выпадающем списке
combobox_currency.set('bitcoin')

# Создание метки для отображения полного названия криптовалюты
label_name = tk.Label(root)
label_name.pack(padx=10, pady=10)  # Размещение метки в окне с отступами

# Создание метки для отображения результата
label_entry = tk.Label(root)
label_entry.pack(padx=10, pady=10)  # Размещение метки в окне с отступами

# Создание кнопки для получения курса обмена
tk.Button(root, text='Получить курс обмена', width=30, height=3,
          command=get_exchange_rate).pack(padx=10, pady=10)

# Запуск главного цикла приложения
root.mainloop()
