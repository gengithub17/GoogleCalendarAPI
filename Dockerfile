FROM python:3.11.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app/ /app/
RUN python accountSetting.py

CMD ["python", "main.py"]