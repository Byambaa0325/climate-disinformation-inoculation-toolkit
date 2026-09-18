# Climate Disinformation Lab — Docker Build

# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend-react
COPY frontend-react/package.json frontend-react/package-lock.json* ./
RUN npm ci --legacy-peer-deps
COPY frontend-react/ ./
ENV REACT_APP_API_URL=/api
RUN npm run build

# Stage 2: Python backend + built frontend
FROM python:3.11-slim

WORKDIR /app

# Install core dependencies only
COPY requirements-core.txt ./
RUN pip install --no-cache-dir -r requirements-core.txt

# Copy backend
COPY backend/ ./backend/

# Copy data
COPY data/ ./data/

# Copy built frontend
COPY --from=frontend-builder /app/frontend-react/build ./frontend-react/build

# Non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Environment
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV FLASK_ENV=production

EXPOSE 8080

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "--timeout", "120", "backend.api:app"]
