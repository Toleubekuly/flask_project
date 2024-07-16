FROM python:3-alpine3.12

RUN apk update && apk add --no-cache postgresql-dev gcc python3-dev musl-dev
RUN apk add build-base
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

EXPOSE 4000
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0", "--port=4000"]
