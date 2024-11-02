import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO

# Словарь для сопоставления ID и имени криптовалюты
currency_dict = {}
# Список фиатных валют
fiat_list = ["USD", "EUR", "RUB"]
# Список криптовалют
crypto_list = []


def generate_currency_lists():
    """Функция для генерации списков названий криптовалют и фиатных валют"""
    global crypto_list

    # URL для получения списка криптовалют
    url = "https://api.coingecko.com/api/v3/coins/list"
    headers = {"accept": "application/json"}  # Заголовки для запроса
    try:
        # Выполнение HTTP-запроса
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на успешность запроса
        data = response.json()  # Преобразование ответа в JSON-формат
        for coin in data:
            crypto_list.append(coin['name'])  # Извлечение ID криптовалюты
            # Сохранение имени криптовалюты в словаре
            currency_dict[coin['name']] = coin['id']
    except requests.RequestException as e:
        print(f"Ошибка при получении списка криптовалют: {e}")


def get_exchange_rate():
    """Функция для получения курса обмена криптовалюты"""
    base_name = combobox_crypto.get()  # Получение выбранной криптовалюты
    target_code = combobox_fiat.get().lower()  # Получение выбранной фиатной валюты

    if not base_name or not target_code:
        label_entry.config(text='Неверное название валюты',
                           font=('Arial', 12), fg='red')
        return
    base_code = currency_dict.get(base_name)
    # Обновление метки с полным названием криптовалюты
    if base_code :
        label_name.config(text=f'Выбранная криптовалюта: {base_name}',
                          font=('Arial', 12), fg='black')
        update_coin_image(base_code)
        update_flag(target_code)
    else:
        label_name.config(text='Криптовалюта не найдена',
                          font=('Arial', 12), fg='red')
        return

    # URL для получения курса обмена
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={
        base_code}&vs_currencies={target_code}"
    headers = {"accept": "application/json"}  # Заголовки для запроса
    try:
        # Выполнение HTTP-запроса
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на успешность запроса
        data = response.json()  # Преобразование ответа в JSON-формат
        if base_code in data:
            # Извлечение курса обмена
            exchange_rate = data[base_code][target_code]
            label_entry.config(text=f'Курс обмена {base_code.upper()} к {target_code.upper()}: {exchange_rate}',
                               font=('Arial', 12), fg='black')
        else:
            label_entry.config(text='Отсутствуют данные торгов',
                               font=('Arial', 12), fg='red')
    except requests.RequestException as e:
        label_entry.config(text=f'Ошибка: {e}', font=('Arial', 12), fg='red')
    except KeyError as ex:
        label_entry.config(text=f'Ошибка: Эта криптовалюта не торгуется через {ex}',
                           font=('Arial', 12), fg='red')


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
        image_url = data.get('image', {}).get('small', '')
        if image_url:
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                # Преобразование содержимого ответа в байты
                img_data = BytesIO(response.content)
                img = Image.open(img_data)  # Открытие изображения
                img.thumbnail((50, 50), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                label_image.config(image=img_tk)
                # Сохранение ссылки на изображение, чтобы оно не было удалено сборщиком мусора
                label_image.image = img_tk
            except requests.RequestException as e:
                print(f"Ошибка при загрузке изображения: {e}")
    except requests.RequestException as e:
        print(f"Ошибка при получении данных криптовалюты: {e}")


def update_flag(src):
    """Функция для обновления изображения флага страны"""
    img = Image.open(f'imgs/{src.lower()}.png')
    img.thumbnail((50, 50), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    label_image2.config(image=img_tk)
    # Сохранение ссылки на изображение, чтобы оно не было удалено сборщиком мусора
    label_image2.image = img_tk

# Функция фильтрует варианты в выпадающем списке по введенному тексту


def filter_currencies(event, combobox, crypto_list):
    # Преобразуем введенный текст в нижний регистр
    search_text = event.widget.get().lower()
    filtered_list = [
        f'{coin}' for coin in crypto_list if search_text in coin.lower()]
    combobox['values'] = filtered_list
    # Автоматическое открытие выпадающего списка
    combobox.event_generate('<Down>')


# Создание главного окна приложения
root = tk.Tk()
root.title('Курсы обмена криптовалют')  # Установка заголовка окна
root.geometry('500x500')  # Установка размеров окна

# Генерация списков названий криптовалют и фиатных валют
generate_currency_lists()

# Создание метки для инструкции по выбору криптовалюты
label_crypto = tk.Label(root, text='Выберите криптовалюту:')
label_crypto.pack(pady=[10, 10])  # Размещение метки в окне с отступами

# Создание выпадающего списка для выбора криптовалюты
combobox_crypto = ttk.Combobox(root, values=crypto_list, height=30, width=30)
# Размещение выпадающего списка в окне с отступами
combobox_crypto.pack(pady=[10, 10])
# Установка значения по умолчанию в выпадающем списке
combobox_crypto.set('Idena')
# Привязываем функцию фильтрации к событию отпускания клавиш
combobox_crypto.bind('<KeyRelease>', lambda event: filter_currencies(
    event, combobox_crypto, crypto_list))

# Создание метки для инструкции по выбору фиатной валюты
label_fiat = tk.Label(root, text='Выберите фиатную валюту:')
label_fiat.pack(pady=[10, 10])  # Размещение метки в окне с отступами

# Создание выпадающего списка для выбора фиатной валюты
combobox_fiat = ttk.Combobox(root, values=fiat_list, height=30, width=30)
# Размещение выпадающего списка в окне с отступами
combobox_fiat.pack(pady=[10, 10])
combobox_fiat.set('USD')  # Установка значения по умолчанию в выпадающем списке

# Создание метки для отображения полного названия криптовалюты
label_name = tk.Label(root)
label_name.pack(padx=10, pady=10)  # Размещение метки в окне с отступами

# Создание метки для отображения изображения криптовалюты
label_image = tk.Label(root)
label_image.pack(padx=10, pady=10)  # Размещение метки в окне с отступами

# Создание метки для отображения флага страны
label_image2 = tk.Label(root)
label_image2.pack(padx=10, pady=10)  # Размещение метки в окне с отступами

# Создание метки для отображения результата
label_entry = tk.Label(root)
label_entry.pack(padx=10, pady=10)  # Размещение метки в окне с отступами

# Создание кнопки для получения курса обмена
tk.Button(root, text='Получить курс обмена', width=30, height=3,
          command=get_exchange_rate).pack(padx=10, pady=10)

# Запуск главного цикла приложения
root.mainloop()
