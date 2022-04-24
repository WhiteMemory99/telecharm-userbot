FROM python:3.10.4-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export --output requirements.txt --without-hashes --extras fast

FROM python:3.10.4-slim

WORKDIR /userbot

COPY --from=requirements-stage /tmp/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

CMD ["python", "-m", "app"]