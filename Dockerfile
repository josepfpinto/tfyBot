# syntax=docker/dockerfile:1

FROM public.ecr.aws/lambda/python:3.11

COPY . .

RUN pip install -r requirements.txt gunicorn


CMD ["gunicorn", "-b", ":8000", "app:app"]