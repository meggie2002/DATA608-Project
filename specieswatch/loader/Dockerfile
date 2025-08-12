FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libpq-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /loader

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "push_to_db.py"]
