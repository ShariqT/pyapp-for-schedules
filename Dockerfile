FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /app
WORKDIR /app
COPY ./scheduleapp ./scheduleapp
COPY ./api ./api
COPY ./manage.py ./manage.py
COPY ./pyproject.toml ./pyproject.toml
RUN pip install uv
RUN uv sync
RUN uv run manage.py migrate
EXPOSE 8000
CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]
