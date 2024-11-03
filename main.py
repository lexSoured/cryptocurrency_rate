import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO

# Словарь для сопоставления ID и имени криптовалюты
currency_dict = {}
# Список фиатных валют
fiat_list = ['USD', 'EUR', 'RUB']
# Список криптовалют
crypto_list = []


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
            crypto_list.append(coin['name'])  # Извлечение ID криптовалюты
            # Сохранение имени криптовалюты в словаре
            currency_dict[coin['name']] = coin['id']
    except requests.RequestException as e:
        messagebox.showerror(
            'Ошибка', f'Ошибка при получении списка криптовалют: {e}')


def get_exchange_rate(event=None):
    '''Функция для получения курса обмена криптовалюты'''
    base_name = combobox_crypto.get()  # Получение выбранной криптовалюты
    target_code = combobox_fiat.get().lower()  # Получение выбранной фиатной валюты

    if not base_name or not target_code:
        messagebox.showwarning('Предупреждение', 'Неверное название валюты')
        return
    base_code = currency_dict.get(base_name)
    # Обновление метки с полным названием криптовалюты
    if base_code:
        label_name.config(text=f'Выбранная криптовалюта:\n\t {base_name}')
        label_name2.config(text=f'Выбранная фиатная валюта:\n\t {
                           target_code.upper()}')

        update_coin_image(base_code)
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
                               target_code.upper()}: {exchange_rate}')
        else:
            label_entry.config(text='Отсутствуют данные торгов')
    except requests.RequestException as e:
        messagebox.showerror('Ошибка', f'{e}')
    except KeyError:
        messagebox.showerror('Ошибка', 'Эта криптовалюта не торгуется')


def update_coin_image(coin_id):
    '''Функция для обновления изображения криптовалюты'''
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
    headers = {'accept': 'application/json'}  # Заголовки для запроса
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
                messagebox.showerror(
                    'Ошибка', f'Ошибка при загрузке изображения: {e}')
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
root.geometry(f'600x500+{root.winfo_screenwidth()//2 -
              300}+{root.winfo_screenheight()//2-250}')  # Установка размеров окна
# Установка прозрачности и всегда поверх других окон
root.attributes('-alpha', 0.9, '-topmost', True)
root.config(bg='#1aa698', borderwidth=12, border=5, padx=20,
            pady=20)  # Настройка фона и границ окна
# Генерация списков названий криптовалют и фиатных валют
generate_currency_lists()
# Настройка веса колонок и строк
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)

style = ttk.Style()
style.configure(
    'TLabel',  # Имя стиля
    foreground='#fefe2e',  # Цвет текста
    background='#1aa698',  # Цвет фона
    font=('Roboto', 12, 'bold'),  # Шрифт
    padding=(10, 10),  # Отступы (горизонтальный, вертикальный)
)

# Создание метки для инструкции по выбору криптовалюты
label_crypto = ttk.Label(
    root,
    style='TLabel',
    text='Выберите криптовалюту\n (Можно воспользоваться\n вводом с клавиатуры):',
)
# Размещение метки в окне с отступами
label_crypto.grid(column=0, row=0, sticky='nw')

# Создание метки для инструкции по выбору фиатной валюты
label_fiat = ttk.Label(root, style='TLabel', text='Выберите фиатную валюту:')
# Размещение метки в окне с отступами
label_fiat.grid(column=1, row=0, sticky='ne')

# Создание метки для отображения полного названия криптовалюты
label_name = ttk.Label(root, style='TLabel')
label_name.grid(column=0, row=2)  # Размещение метки в окне с отступами

# Создание метки для отображения полного названия фиатной валюты
label_name2 = ttk.Label(root, style='TLabel')
label_name2.grid(column=1, row=2)  # Размещение метки в окне с отступами

# Создание метки для отображения изображения криптовалюты
label_image = ttk.Label(root, style='TLabel')
label_image.grid(column=0, row=3)  # Размещение метки в окне с отступами

# Создание метки для отображения флага страны
label_image2 = ttk.Label(root, style='TLabel')
label_image2.grid(column=1, row=3)  # Размещение метки в окне с отступами

# Создание метки для отображения результата
label_entry = ttk.Label(root, style='TLabel')
# Размещение метки в окне с отступами
label_entry.grid(column=0, row=4, columnspan=2)

style.configure(
    'TCombobox',  # Имя стиля
    foreground='#8626b5',  # Цвет текста
    font=('Roboto', 16, 'bold'),  # Шрифт
    padding=(10, 10),  # Отступы (горизонтальный, вертикальный)
    arrowsize=12,  # Размер стрелки
)

# Создание выпадающего списка для выбора криптовалюты
combobox_crypto = ttk.Combobox(root, style='TCombobox', values=crypto_list)
# Размещение выпадающего списка в окне с отступами
combobox_crypto.grid(column=0, row=1, pady=15, padx=10, sticky='nw')
# Установка значения по умолчанию в выпадающем списке
combobox_crypto.set('Idena')
# Привязка функции к нажатию Enter
combobox_crypto.bind('<Return>', get_exchange_rate)
combobox_crypto.bind('<KeyRelease>', lambda event: filter_currencies(
    # Привязка функции фильтрации к событию отпускания клавиш
    event, combobox_crypto, crypto_list))

# Создание выпадающего списка для выбора фиатной валюты
combobox_fiat = ttk.Combobox(
    root, style='TCombobox', values=fiat_list, state='readonly')
# Размещение выпадающего списка в окне с отступами
combobox_fiat.grid(column=1, row=1, pady=15, padx=10, sticky='ne')
combobox_fiat.set('USD')  # Установка значения по умолчанию в выпадающем списке

# Создание кнопки для получения курса обмена
button = tk.Button(
    root,
    text='Получить курс обмена',
    fg='#fefe2e',
    bg='#1d655e',
    activebackground='#00ce00',
    activeforeground='#fff2e2',
    font=('Arial', 12, 'bold'),
    padx=15,
    pady=10,
    relief='raised',
    borderwidth=3,
    command=get_exchange_rate,
)
# Размещение кнопки в окне с отступами
button.grid(column=0, row=5, columnspan=2, sticky='s')

# Запуск главного цикла приложения
root.mainloop()
