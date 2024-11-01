import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO

currency_dict = {}  # Словарь для сопоставления ID и имени криптовалюты


def generate_currency_list():
    """Функция для генерации списка названий криптовалют"""
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
    """Функция для получения курса обмена криптовалюты"""
    target_code = combobox_currency.get().lower(
    )  # Получение выбранной криптовалюты и преобразование в нижний регистр
    if not target_code:
        label_entry.config(text='Неверное название валюты', font=(
            'Arial', 12), fg='red')  # Сообщение об ошибке, если поле пустое
        return

    # Обновление метки с полным названием криптовалюты
    if target_code in currency_dict:
        label_name.config(text=f'Выбранная криптовалюта: {
                          currency_dict[target_code]}', font=('Arial', 12), fg='black')
        update_coin_image(target_code)
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


def update_coin_image(coin_id):
    """Функция для обновления изображения криптовалюты"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    headers = {"accept": "application/json"}  # Заголовки для запроса
    try:
        # Выполнение HTTP-запроса
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на успешность запроса
        data = response.json()  # Преобразование ответа в JSON-формат
        # Получение ссылки на маленькое изображение
        image_url = data.get('image', {}).get('thumb', '')
        if image_url:
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                img_data = BytesIO(response.content)  # Преобразование содержимого ответа в байты
                # Изменение размера изображения
                img = Image.open(img_data)  # Открытие изображения
                img_tk = ImageTk.PhotoImage(img)
                label_image.config(image=img_tk)
                img.thumbnail((30,30), Image.Resampling.LANCZOS)  # Изменение размера изображения
                # Сохранение ссылки на изображение, чтобы оно не было удалено сборщиком мусора
                label_image.image = img_tk
            except requests.RequestException as e:
                print(f"Ошибка при загрузке изображения: {e}")
    except requests.RequestException as e:
        print(f"Ошибка при получении данных криптовалюты: {e}")


# Создание главного окна приложения
root = tk.Tk()
root.title('Курсы обмена криптовалют')  # Установка заголовка окна
root.geometry('500x350')  # Установка размеров окна

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

# Создание метки для отображения изображения криптовалюты
label_image = tk.Label(root)
label_image.pack(padx=10, pady=10)  # Размещение метки в окне с отступами

# Создание метки для отображения результата
label_entry = tk.Label(root)
label_entry.pack(padx=10, pady=10)  # Размещение метки в окне с отступами

# Создание кнопки для получения курса обмена
tk.Button(root, text='Получить курс обмена', width=30, height=3,
          command=get_exchange_rate).pack(padx=10, pady=10)

# Запуск главного цикла приложения
root.mainloop()
