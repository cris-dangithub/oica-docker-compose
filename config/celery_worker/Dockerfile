FROM python:3.12-alpine

WORKDIR /usr/src/app

# Install system dependencies required for:
# - WeasyPrint (cairo, pango, gdk-pixbuf, etc.)
# - psycopg2-binary (postgresql-dev, gcc, python3-dev, musl-dev)
# - Pillow for image processing (jpeg, zlib, freetype, etc.)
# - Fonts for PDF generation
RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev \
    python3-dev \
    glib-dev \
    gobject-introspection-dev \
    pango-dev \
    gdk-pixbuf-dev \
    libffi-dev \
    cairo-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    harfbuzz-dev \
    fribidi-dev \
    fontconfig \
    ttf-dejavu \
    ttf-liberation \
    font-noto

# Copy requirements.txt from build context (services/backend/)
# NOTE: This file should be synced from config/celery_worker/requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run Celery worker
# Using python -m ensures celery is found in the Python environment
CMD ["python", "-m", "celery", "-A", "celery_worker", "worker", "--loglevel=info"]
