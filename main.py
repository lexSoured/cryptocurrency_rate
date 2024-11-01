import tkinter as tk
import requests


def get_exchange_rate():
    # Преобразуем в нижний регистр для соответствия API
    target_code = entry.get().lower()
    if target_code:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={
            target_code}&vs_currencies=usd"
        headers = {"accept": "application/json"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if target_code in data:
                exchange_rate = data[target_code]['usd']
                entry_label.config(text=f'Курс обмена {
                                   target_code.upper()} к USD: {exchange_rate}')
            else:
                entry_label.config(text='Неверное название валюты')
        else:
            entry_label.config(text=f'Ошибка при выполнении запроса: {
                               response.status_code}')
    else:
        entry_label.config(text='Введите код валюты')


root = tk.Tk()
root.title('Курсы обмена криптовалют')
root.geometry('500x250')

# Метка и поле ввода для количества валюты
entry_label = tk.Label(root, text='Введите название криптовалюты')
entry_label.pack(padx=10, pady=10)

entry = tk.Entry(root)
entry.pack(padx=10, pady=10)

entry.insert(0, 'bitcoin')  # Устанавливаем значение по умолчанию

tk.Button(root, text='Получить курс обмена', width=30, height=3,
          command=get_exchange_rate).pack(padx=10, pady=10)

root.mainloop()
