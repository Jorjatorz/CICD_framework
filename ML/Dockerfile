FROM python:3.8

WORKDIR /framework

COPY src src/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY builder.sh .
RUN chmod 777 builder.sh

COPY scheduler.py .

CMD ["python3", "scheduler.py"]