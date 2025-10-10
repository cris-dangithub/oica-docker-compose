FROM python:3.13.7-alpine

WORKDIR /usr/src/app

# Install system dependencies required for WeasyPrint
RUN apk add --no-cache \
    glib-dev \
    gobject-introspection-dev \
    pango-dev \
    gdk-pixbuf-dev \
    libffi-dev \
    cairo-dev \
    gcc \
    musl-dev \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    harfbuzz-dev \
    fribidi-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./server.py" ]

