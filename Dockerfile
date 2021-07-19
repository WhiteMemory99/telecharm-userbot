FROM python:3.9.6

ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV PATH "/code:${PATH}"

WORKDIR /code

RUN pip install poetry

RUN apt-get update && apt-get install -y python3-opencv && rm -rf /var/lib/apt/lists/*

COPY poetry.lock pyproject.toml /code/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi -E opencv -E speedup

COPY . /code/

CMD ["python", "-m", "app"]