FROM python:3.11-slim AS builder

RUN apt-get -y update \
    && apt-get -y upgrade \
    && pip install poetry==1.7.0

COPY . /src/

WORKDIR /src/

RUN python -m poetry config virtualenvs.in-project true \
    && python -m poetry config virtualenvs.create true \
    && python -m poetry install --only main


FROM gcr.io/distroless/python3-debian12:nonroot

COPY --from=builder /src/.venv/lib/python3.11/site-packages/ /usr/lib/python3.11/

CMD ["-m", "bruhsty"]
