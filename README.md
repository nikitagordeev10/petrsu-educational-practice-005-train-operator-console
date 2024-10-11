# Установка зависимостей

```bash
pip3 freeze > requirements.txt  # Python3
pip freeze > requirements.txt    # Python2

train_control_panel/
│
├── app/
│   ├── __init__.py                      # Инициализация приложения
│   ├── models.py                        # Модели и бизнес-логика (состояние поезда)
│   ├── controllers.py                   # Контроллеры (обработка команд пользователя)
│   ├── services/
│   │   ├── __init__.py                  # Инициализация сервисов
│   │   ├── audio_service.py             # Логика работы со звуками
│   │   ├── telemetry_service.py         # Телеметрия: расчеты скорости, пробега и топлива
│   │   ├── logging_service.py           # Логирование событий
│   │   └── speech_recognition_service.py # Новый модуль для распознавания речи
│   └── views/
│       ├── __init__.py                  # Инициализация графического интерфейса
│       ├── main_view.py                 # Основной интерфейс пользователя
│       └── widgets.py                   # Индивидуальные виджеты (кнопки, индикаторы)
│
├── data/                                  # Хранение базы данных и файлов
│   └── train_control.db                   # Файл базы данных SQLite
│
├── db/                                    # Модуль работы с базой данных
│   ├── __init__.py
│   ├── models.py                          # Определение моделей данных
│   ├── schema.sql                         # SQL скрипт для инициализации БД (если не используем ORM)
│   └── db_manager.py                      # Управление базой данных (создание, чтение, обновление)
│
├── ml/
│   ├── __init__.py
│   ├── voice_command_model.py             # Нейронная сеть для голосовых команд
│   └── train_model.py                     # Скрипт для обучения модели
│
├── resources/                             # Ресурсы: изображения, звуки
│   ├── sounds/
│   └── images/
│
├── tests/                                 # Тесты
│   ├── __init__.py
│   ├── test_models.py                     # Тестирование моделей
│   ├── test_services.py                   # Тестирование сервисов
│   └── test_views.py                      # Тестирование интерфейса
│
├── main.py                                # Точка входа в приложение
└── requirements.txt                       # Зависимости проекта
