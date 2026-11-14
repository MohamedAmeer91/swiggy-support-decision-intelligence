FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt common.py README.md ./
COPY data ./data
COPY outputs ./outputs
COPY web ./web
RUN pip install --no-cache-dir numpy==1.26.4 -r web/requirements.txt
EXPOSE 8000
CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]
