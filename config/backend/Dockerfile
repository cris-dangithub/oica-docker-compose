FROM python:3.12-alpine
WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg
RUN apk add --no-cache pango cairo gdk-pixbuf harfbuzz fribidi libffi \
    libstdc++ libgcc fontconfig ttf-dejavu ttf-liberation font-noto
COPY config/backend/*.txt /tmp/config/backend/
RUN --mount=type=cache,target=/root/.cache/pip apk add --no-cache --virtual .build-deps gcc musl-dev && pip install -r /tmp/config/backend/requirements.txt && apk del .build-deps
COPY backend/ ./
COPY scripts/migrate.py scripts/interrupt_jobs.py ./scripts/
COPY config/backend/migrations/ ./migrations/
RUN addgroup -g 10001 oica && adduser -D -u 10001 -G oica oica \
    && mkdir -p /usr/src/app/data/filestore && chown -R oica:oica /usr/src/app
USER oica
CMD ["python", "server.py"]
