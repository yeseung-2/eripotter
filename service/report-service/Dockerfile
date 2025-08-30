FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치: 지금은 불필요하므로 제거 가능
# RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/* && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY __init__.py .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

EXPOSE 8007
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
