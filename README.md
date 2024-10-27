# ParticipantsApp

## Описание проекта

`ParticipantsApp` — это веб-приложение для управления участниками, предоставляющее возможности регистрации,
взаимодействия и поиска участников. Проект реализован на FastAPI и поддерживает фильтрацию участников по параметрам, а
также функцию оценки, которая может приводить к «взаимной симпатии» между участниками. В приложении предусмотрено
асинхронное наложение водяного знака на аватар пользователя и определение геолокации по названию города.

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/melixz/ParticipantsApp
   ```

2. Настройте переменные окружения в файле .env:

   ```bash
   DATABASE_URL=sqlite+aiosqlite:///./test.db
   BASE_URL="http://127.0.0.1:8000"
   
   ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Соберите и запустите приложение с использованием Docker:

   ```bash
   docker build -t participantsapp .
   docker run -p 80:80 participantsapp
   ```

5. Приложение запустится на `http://127.0.0.1`.

## Технологии

- Python 3.12+
- FastAPI: для создания и управления API
- SQLAlchemy + PostgreSQL: для работы с базой данных
- HTTPX: для работы с внешними API (геолокация)
- Pydantic: для валидации данных и схем
- Docker: для контейнеризации приложения
- AsyncIO: для асинхронной обработки запросов и наложения водяного знака

## Текущие возможности

- **Регистрация нового участника** с обработкой аватарки и наложением водяного знака.
- **Оценка другого участника** с возможностью отслеживания взаимных симпатий и отправки уведомлений.
- **Список участников** с возможностью фильтрации по параметрам, сортировки и поиска по расстоянию от заданных
  координат.
- **Геолокация участников** по указанному городу с автоматическим определением широты и долготы через Nominatim API.

## Команды API

- `POST /api/clients/create` — Регистрация нового участника.
- `POST /api/clients/{id}/match` — Оценка другого участника.
- `GET /api/clients/list` — Получение списка участников с фильтрацией, сортировкой и поддержкой поиска по расстоянию.

## Преимущества

- **Асинхронная обработка**: Использование асинхронных функций для повышения производительности и улучшения отклика API.
- **Геолокация по городу**: Автоматическое определение координат по названию города для точного поиска участников.
- **Лимит оценок**: Настраиваемый лимит оценок в день для предотвращения злоупотреблений.
- **Уведомления о взаимной симпатии**: При обнаружении взаимного интереса пользователи получают уведомление с контактной
  информацией.

## Цель проекта

Проект создан для организации базы данных участников и предоставления инструментов для их взаимодействия и поиска.
Приложение поддерживает взаимодействие через REST API, не требуя веб-интерфейса, и ориентировано на создание удобного и
эффективного функционала для пользователей.

## Дополнительные задачи

- **Взаимная симпатия**: Отправка почтовых уведомлений участникам при взаимной симпатии (возможность доработки).
- **Кэширование запросов расстояния**: Возможность интеграции кэширования результатов для оптимизации повторных запросов
  с одинаковыми параметрами.

## Ссылки

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Nominatim API](https://nominatim.org/release-docs/develop/api/Search/)
- [ParticipantsApp на Railway](https://participantsapp-production.up.railway.app/docs)
