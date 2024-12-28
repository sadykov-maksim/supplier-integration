# Этап, на котором выполняются подготовительные действия
FROM python:3.12.2 as builder
LABEL authors="Builder"

WORKDIR /installer

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt update && \
    apt install -y --no-install-recommends gcc


RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY service/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install brom

# Финальный этап
FROM python:3.12.2
LABEL authors="Developer"

RUN apt update &&  \
    apt install -y netcat-traditional && \
    apt install -y locales

ENTRYPOINT ["RUN apt instal -y netcat-traditional"]

COPY --from=builder /opt/venv /opt/venv
COPY compatibility ./opt/
COPY postgresql ./postgresql/

WORKDIR /service

ENV PATH="/opt/venv/bin:$PATH"
ENV PGSERVICEFILE /postgresql/.pg_service.conf
ENV PGPASSFILE /postgresql/.pgpass

COPY service .
COPY service/entrypoint.sh entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["sh", "-c", "/service/entrypoint.sh"]