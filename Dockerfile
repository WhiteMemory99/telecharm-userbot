FROM python:3.10.1-slim-buster

ENV PYTHONPATH "${PYTHONPATH}:/userbot"
ENV PATH "/userbot:${PATH}"

WORKDIR /userbot

RUN set +x \
 && apt update \
 && apt install -y curl gcc git \
 && curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python - \
 && cd /usr/local/bin \
 && ln -s /opt/poetry/bin/poetry \
 && poetry config virtualenvs.create false \
 && rm -rf /var/lib/apt/lists/*

COPY . .

RUN poetry install --no-interaction --no-ansi --no-dev -E fast

CMD ["python", "-m", "app"]