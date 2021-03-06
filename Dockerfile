FROM python:3.7
COPY . /usr/src/app

COPY . .
RUN pip install -r requirements.txt

CMD ["python", "app"]

EXPOSE 3001