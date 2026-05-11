FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# systémové balíčky (kvôli psycopg2 a pod.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# projekt
COPY . /app/

# statické súbory
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD python manage.py makemigrations && python manage.py migrate && daphne -b 0.0.0.0 -p ${PORT:-8080} DanceScheduleWeb.asgi:application
