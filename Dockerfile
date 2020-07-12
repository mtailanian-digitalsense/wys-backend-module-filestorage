FROM python:3
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8085
COPY . .
CMD [ "gunicorn", "--bind", "0.0.0.0:8085", "main:app" ]
