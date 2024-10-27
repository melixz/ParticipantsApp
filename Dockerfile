# Используем базовый образ Python
FROM python:latest

# Настраиваем буферизацию, чтобы Python выводил данные сразу
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем virtualenv и создаем виртуальное окружение
RUN pip install --no-cache-dir virtualenv && \
    virtualenv venv

# Копируем requirements.txt из volume и устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
RUN ./venv/bin/pip install -r requirements.txt

# Копируем все остальное приложение
COPY . .

# Добавляем виртуальное окружение в PATH
ENV PATH="/app/venv/bin:$PATH"

# Команда для запуска приложения
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
