FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
ENV DB_USER=root
ENV DB_PASS=your_db_password
ENV DB_NAME=todo_app
ENV DB_HOST=your_db_public_ip

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]