FROM python:3.11-slim AS base

SHELL ["/bin/bash", "-c"]

ENV PATH="/poetry-venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_OPTIONS_NO_PIP=1 \
    POETRY_VIRTUALENVS_OPTIONS_NO_SETUPTOOLS=1

WORKDIR /project

RUN --mount=type=cache,target=/poetry-venv \
    --mount=target=/var/lib/apt/lists,type=cache \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt-get -y update \
    && apt-get -y upgrade \
    && python -m venv /poetry-venv \
    && source /poetry-venv/bin/activate \
    && pip install poetry

RUN --mount=target=/var/lib/apt/lists,type=cache \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=cache,target=/poetry-venv \
    poetry lock \
    && poetry install --only main --no-root

FROM gcr.io/distroless/python3-debian12:nonroot as final

COPY --from=base \
    /project/.venv/lib/python3.11/site-packages/ /home/nonroot/.local/lib/python3.11/site-packages/

ENV PYTHONPATH="${PYTHONPATH}:/project/src" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY . /project

CMD ["-m", "app", "--config", "./config/config.yaml"]
