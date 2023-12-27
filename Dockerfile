FROM python:3.11.3

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./api .

CMD ["uvicorn", "api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]