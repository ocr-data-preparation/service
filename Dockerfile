FROM python:3.7
COPY . /usr/src/app

COPY . .
RUN pip install -r requirements.txt

EXPOSE 3001

CMD ["python", "app"]