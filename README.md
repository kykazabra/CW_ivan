# Проект: Бот-нутрициолог
https://t.me/nutrition_consultant_pro_bot

## Описание

Этот проект представляет собой Telegram-бота, который предоставляет консультации по нутрициологии. Бот использует современные технологии машинного обучения и обработки естественного языка, включая LangChain и LangGraph, для обработки запросов пользователей, обращения к базе знаний и поиска информации в интернете. Бот способен классифицировать запросы, отвечать на основе базы знаний, запрашивать дополнительную информацию у пользователя или выполнять веб-поиск.

Основные возможности:
- Ответы на вопросы по нутрициологии с использованием LLM (модель `gpt-4o-mini`).
- Интеграция с базой знаний через RAG (Retrieval-Augmented Generation).
- Веб-поиск через API Tavily.
- Логирование взаимодействий через LangSmith.
- Хранение истории чата и состояния в SQLite.

## Требования

Для работы проекта необходимы следующие зависимости, указанные в `requirements.txt`:

- Python 3.11
- LangChain и связанные библиотеки (`langchain`, `langchain-community`, `langchain-openai`, `langgraph`, etc.)
- `pyTelegramBotAPI` и `telebot` для работы с Telegram API
- `python-docx` для обработки документов Word
- `PyYAML` для работы с конфигурацией
- `telegramify-markdown` для форматирования сообщений
- `pytest` для тестирования
- Прочие зависимости: `pydantic`, `typing_extensions`, `urllib3`

Полный список зависимостей находится в файле `requirements.txt`.

## Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone <URL_репозитория>
   cd <папка_проекта>
   ```

2. **Создайте виртуальное окружение** (опционально, но рекомендуется):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Windows: venv\Scripts\activate
   ```

3. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте конфигурацию**:
   - Скопируйте файл `config.example.yaml` в `config.yaml`:
     ```bash
     cp config.example.yaml config.yaml
     ```
   - Отредактируйте `config.yaml`, указав:
     - API-ключ для LLM (например, OpenAI или его прокси).
     - Токен Telegram-бота.
     - API-ключ для Tavily.
     - Ключи и настройки для LangSmith (если используется).

5. **Подготовьте базу знаний** (опционально):
   - Поместите документ Word с информацией о нутрициологии в папку `data` (например, `готовые схемы.docx`).
   - Запустите скрипт `src/utils/update_rag.py` для создания векторной базы знаний:
     ```bash
     python src/utils/update_rag.py
     ```

6. **Запустите бота**:
   ```bash
   python src/main.py
   ```

## Использование

1. Запустите бота, выполнив команду выше.
2. В Telegram найдите бота по его токену или имени и начните общение, отправив команду `/start`.
3. Задавайте вопросы по нутрициологии, например:
   - "Какие продукты полезны для сердца?"
   - "Что такое кето-диета?"
4. Бот классифицирует ваш запрос и:
   - Ответит на основе базы знаний (если вопрос связан с нутрициологией).
   - Выполнит веб-поиск (для рекомендаций товаров или актуальной информации).
   - Запросит дополнительную информацию, если запрос неясен.
   - Дает свободный ответ для вопросов, не связанных с нутрициологией.

## Структура проекта

- **`data/`**: Хранит базу данных (`memory_store.db`), векторную базу знаний (`doc_rag/chroma.sqlite3`) и документы Word.
- **`src/`**: Исходный код приложения:
  - `agent/`: Логика работы агента (граф LangGraph, промпты, инструменты).
  - `bot/`: Логика Telegram-бота.
  - `utils/`: Утилиты для работы с конфигурацией и обновления базы знаний.
  - `main.py`: Точка входа приложения.
- **`tests/`**: Тесты для проверки функциональности.
- **`Dockerfile`**: Для контейнеризации приложения.
- **`config.yaml`**: Конфигурация приложения (API-ключи, настройки LLM, пути к БД).
- **`requirements.txt`**: Список зависимостей.

## Контейнеризация

Проект можно запустить в Docker-контейнере:

1. **Соберите образ**:
   ```bash
   docker build -t nutrition-bot .
   ```

2. **Запустите контейнер**:
   ```bash
   docker run -v $(pwd)/data:/app/data nutrition-bot
   ```

   Примечание: Убедитесь, что папка `data` содержит необходимые файлы (например, `config.yaml`, `готовые схемы.docx`).

## Тестирование

Для запуска тестов используйте `pytest`:
```bash
pytest tests/
```

Тесты проверяют:
- Корректность работы графа (`test_graph.py`).
- Функциональность Telegram-бота (`test_tg_bot.py`).
- Инициализацию инструментов (`test_tools.py`).

## Логирование

Проект использует LangSmith для логирования взаимодействий. Убедитесь, что в `config.yaml` указаны корректные ключи и настройки для `langsmith`.

## Ограничения

- Бот ожидает ответа пользователя в течение ограниченного времени (настраивается в `tick_limit` и `tick_time` в `tg_bot.py`).
- Векторная база знаний создается на основе документов Word, разделенных по заголовкам (жирный шрифт).
- Для работы требуется стабильное интернет-соединение для обращения к API (LLM, Tavily, LangSmith).
