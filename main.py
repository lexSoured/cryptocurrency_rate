import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import os

# Словарь для сопоставления ID и имени - символа криптовалюты
currency_dict = {}
# Список фиатных валют
fiat_list = ['USD', 'EUR', 'RUB']
# Множество криптовалют
crypto_list = set()


def generate_currency_lists():
    '''Функция для генерации списков названий криптовалют и фиатных валют'''
    global crypto_list

    # URL для получения списка криптовалют
    url = 'https://api.coingecko.com/api/v3/coins/list'
    headers = {'accept': 'application/json'}  # Заголовки для запроса
    try:
        # Выполнение HTTP-запроса
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на успешность запроса
        data = response.json()  # Преобразование ответа в JSON-формат
        for coin in data:
            # Добавление названия криптовалюты в множество
            crypto_list.add(f'{coin['name']} ({coin['symbol']})')
            # Сохранение имени и id криптовалюты в словаре для дальнейшего использования
            currency_dict[coin['symbol']] = (coin['name'], coin['id'])

    except requests.RequestException as e:
        messagebox.showerror(
            'Ошибка', f'Ошибка при получении списка криптовалют: {e}')


def get_exchange_rate(event=None):
    '''Функция для получения курса обмена криптовалюты'''
    base_name_symbol = combobox_crypto.get()  # Получение выбранной криптовалюты в формате "Name (Symbol)"
    target_code = combobox_fiat.get().lower()  # Получение выбранной фиатной валюты

    if not base_name_symbol or not target_code:
        messagebox.showwarning('Предупреждение', 'Неверное название валюты')
        return
    # Извлечение символа из строки "Name (Symbol)"
    base_symbol = base_name_symbol.split('(')[-1].replace(')','').strip()
    # Извлечение ID криптовалюты из словаря по символу. Если символ не найден, возращается None
    base_code = currency_dict.get(base_symbol, (None, None))[1]
    # Обновление меток с полными названиями выбранных валют
    if base_code:
        label_name.config(text=f'Выбранная криптовалюта:\n {base_name_symbol}')
        label_name2.config(text=f'Выбранная фиатная валюта:\n {
                           target_code.upper()}')

        update_coin_info(base_code)
        update_flag(target_code)
    else:
        label_name.config(text='Криптовалюта не найдена')
        return

    # URL для получения курса обмена
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={
        base_code}&vs_currencies={target_code}'
    headers = {'accept': 'application/json'}  # Заголовки для запроса
    try:
        # Выполнение HTTP-запроса
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на успешность запроса
        data = response.json()  # Преобразование ответа в JSON-формат
        if base_code in data:
            # Извлечение курса обмена
            exchange_rate = data[base_code][target_code]
            label_entry.config(text=f'Курс обмена {base_code.upper()} к {
                               # 4bcc00')
                               target_code.upper()}: {exchange_rate}', foreground='#4bcc00')
        else:
            label_entry.config(
                text='Отсутствуют данные торгов', foreground='#ff3a33')
    except requests.RequestException as e:
        messagebox.showerror('Ошибка', f'{e}')
    except KeyError:
        messagebox.showerror('Ошибка', 'Эта криптовалюта не торгуется')


def update_coin_info(coin_id):
    '''Функция для обновления данных о валюте'''
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
    headers = {'accept': 'application/json'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Получение ссылки на маленькое изображение криптовалюты
        image_url = data.get('image', {}).get('small', '')
        if image_url:
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img.thumbnail((50, 50), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                label_image.config(image=img_tk)
                label_image.image = img_tk  # Сохранение ссылки на изображение
            except requests.RequestException as e:
                messagebox.showerror(
                    'Ошибка', f'Ошибка при загрузке изображения: {e}')

        # Получение изменения рыночной капитализации
        market_cap_change_percentage_24h = data['market_data']['market_cap_change_percentage_24h']
        if market_cap_change_percentage_24h is not None:
            if market_cap_change_percentage_24h > 0:
                color = 'green'
            else:
                color = 'red'
            label_market_cap_change.config(text=f'Изменение рыночной капитализации за 24 часа: {
                                           market_cap_change_percentage_24h:.2f}%', foreground=color)
    except requests.RequestException as e:
        messagebox.showerror(
            'Ошибка', f'Ошибка при получении данных криптовалюты: {e}')


def update_flag(src):
    '''Функция для обновления изображения флага страны'''
    try:
        img = Image.open(f'imgs/{src.lower()}.png')
        img.thumbnail((50, 50), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        label_image2.config(image=img_tk)
        # Сохранение ссылки на изображение, чтобы оно не было удалено сборщиком мусора
        label_image2.image = img_tk
    except FileNotFoundError:
        pass


def filter_currencies(event, combobox, crypto_list):
    '''Функция фильтрует варианты в выпадающем списке по введенному тексту'''
    # Получаем введенный текст
    search_text = event.widget.get().strip().lower()
    
    # Проверяем, не пустой ли введенный текст и его длина
    if not search_text or len(search_text) < 3:
        # Если текст пустой или его длина меньше 3 символов, сбрасываем список к исходному состоянию
        combobox['values'] = list(crypto_list)
    else:
        # Фильтруем список криптовалют
        filtered_list = [coin for coin in crypto_list if search_text in coin.lower()]
        combobox['values'] = filtered_list
    
    # Автоматическое открытие выпадающего списка
    combobox.event_generate('<Down>')


# Создание главного окна приложения
root = tk.Tk()

root.title('Курсы обмена криптовалют')  # Установка заголовка окна
# Установка размеров и позиции окна
root.geometry(f'600x500+{root.winfo_screenwidth() //
              2 - 300}+{root.winfo_screenheight()//2-250}')
root.config(bg='#0d1217', borderwidth=12, padx=20,
            pady=20)  # Настройка фона и границ окна

# Проверка наличия иконки в папке
icon_path = "imgs/logo.ico"
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)
else:
    pass
# Генерация списков названий криптовалют и фиатных валют
generate_currency_lists()
crypto_list_list = list(crypto_list)
# Настройка веса колонок и строк для правильного расположения элементов
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)

style = ttk.Style()
style.theme_use('alt')
style.configure(
    'TLabel',  # Имя стиля
    foreground='#dfe5ec',  # Цвет текста
    background='#0d1217',  # Цвет фона
    font=('Roboto', 12, 'bold'),  # Шрифт
    padding=(10, 10)  # Отступы (горизонтальный, вертикальный)
)

# Создание метки для инструкции по выбору криптовалюты
label_crypto = ttk.Label(
    root, style='TLabel', text='Выберите криптовалюту\n (Можно воспользоваться\n вводом с клавиатуры):')
# Размещение метки в окне с отступами
label_crypto.grid(column=0, row=0, sticky='nw')

# Создание метки для инструкции по выбору фиатной валюты
label_fiat = ttk.Label(root, style='TLabel', text='Выберите фиатную валюту:')
# Размещение метки в окне с отступами
label_fiat.grid(column=1, row=0, sticky='ne')

# Создание метки для отображения полного названия криптовалюты
label_name = ttk.Label(root, style='TLabel', justify='center')
label_name.grid(column=0, row=2)  # Размещение метки в окне с отступами

# Создание метки для отображения полного названия фиатной валюты
label_name2 = ttk.Label(root, style='TLabel', justify='center')
label_name2.grid(column=1, row=2)  # Размещение метки в окне с отступами

# Создание метки для отображения изображения криптовалюты
label_image = ttk.Label(root, style='TLabel')
label_image.grid(column=0, row=3)  # Размещение метки в окне с отступами

# Создание метки для отображения флага страны
label_image2 = ttk.Label(root, style='TLabel')
label_image2.grid(column=1, row=3)  # Размещение метки в окне с отступами

# Создание метки для отображения изменения рыночной капитализации
label_market_cap_change = ttk.Label(root, style='TLabel')
label_market_cap_change.grid(column=0, row=5, columnspan=2)

# Создание метки для отображения результата
label_entry = ttk.Label(root, style='TLabel')
# Размещение метки в окне с отступами
label_entry.grid(column=0, row=4, columnspan=2)

style.configure(
    'TCombobox',
    fieldbackground='#e5e7eb',  # Цвет фона поля ввода
    background='#35af00',       # Цвет фона кнопки (стрелки)
    foreground='#0d1217',       # Цвет текста
    padding=5,                  # Отступы внутри combobox
    insertwidth=2               # Толщина курсора ввода
)

# Создание выпадающего списка для выбора криптовалюты
combobox_crypto = ttk.Combobox(root, style='TCombobox', values=crypto_list_list,
                               width=30, justify='center', font=('Roboto', 12, 'bold'))
# Размещение выпадающего списка в окне с отступами
combobox_crypto.grid(column=0, row=1, pady=15, padx=10, sticky='nw')
# Установка значения по умолчанию в выпадающем списке
combobox_crypto.set('Idena')
# Привязка функции к нажатию Enter
combobox_crypto.bind('<Return>', get_exchange_rate)
# Привязка функции фильтрации к событию отпускания клавиш
combobox_crypto.bind('<KeyRelease>', lambda event: filter_currencies(
    event, combobox_crypto, crypto_list_list))

# Создание выпадающего списка для выбора фиатной валюты
combobox_fiat = ttk.Combobox(
    root, style='TCombobox', values=fiat_list, state='readonly', width=30, justify='center', font=('Roboto', 12, 'bold'))
# Размещение выпадающего списка в окне с отступами
combobox_fiat.grid(column=1, row=1, pady=15, padx=10, sticky='ne')
# Установка значения по умолчанию в выпадающем списке
combobox_fiat.set('USD')

# Создание кнопки для получения курса обмена
button = tk.Button(
    root,
    text='Получить курс обмена',
    fg='#dfe5ec',
    bg='#239200',
    activebackground='#80e038',
    activeforeground='#e5e7eb',
    font=('Roboto', 12, 'bold'),
    padx=15,
    pady=10,
    relief='raised',
    borderwidth=5,
    command=get_exchange_rate,
)
# Размещение кнопки в окне с отступами
button.grid(column=0, row=6, columnspan=2, sticky='s')

# Запуск главного цикла приложения
root.mainloop()
