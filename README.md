# ВЫПУСКНАЯ АТТЕСТАЦИОННАЯ (ПРОЕКТНАЯ) РАБОТА

#### по программе профессиональной переподготовки
**«Азбука цифры. Программирование на языке Python от базового уровня до продвинутого»**


 ## Курсы обмена криптовалют



**Описание**

Это приложение позволяет пользователям просматривать текущие курсы обмена криптовалют на фиатные валюты. Приложение использует API CoinGecko для получения актуальных данных о курсах обмена и информации о криптовалютах.

**Функциональность**

- Выбор криптовалюты: Пользователь может выбрать криптовалюту из выпадающего списка. Список автоматически фильтруется по вводимому тексту.

- Выбор фиатной валюты: Пользователь может выбрать фиатную валюту из предопределённого списка (USD, EUR, RUB).

- Получение курса обмена: После выбора валют, пользователь может получить текущий курс обмена криптовалюты на фиатную валюту.

- Информация о криптовалюте: Приложение отображает логотип криптовалюты и изменение её рыночной капитализации за последние 24 часа.

- Информация о фиатной валюте: Приложение отображает флаг страны, соответствующей выбранной фиатной валюте.

**Использование**  
- После запуска приложения, вы увидите окно с полем ввода и кнопкой.

- Введите код криптовалюты в поле ввода (например, bitcoin).

- Нажмите кнопку "Получить курс обмена".

- Результат будет отображен под полем ввода.

*Если введен неверный код криптовалюты, будет отображено сообщение "Неверный код валюты".*

*Если произошла ошибка при выполнении запроса, будет отображено сообщение с кодом ошибки.*

**Технологии и библиотеки**  

Python: Язык программирования.  
Tkinter: Библиотека для создания графического интерфейса пользователя.  
Requests: Библиотека для выполнения HTTP-запросов.  
Pillow (PIL): Библиотека для работы с изображениями.  
CoinGecko API: API для получения данных о криптовалютах.  

***Структура проекта***  
app.py: Основной файл приложения.  
imgs/: Директория для хранения изображений флагов стран.  
README.md: Файл с описанием проекта.  
