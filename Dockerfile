# -- Stage 1: Build the React Frontend --
FROM node:18-alpine AS build-frontend
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install

# Pass environment variables to Vite during build time
ARG VITE_CLERK_PUBLISHABLE_KEY
ARG VITE_CLERK_FRONTEND_API
ENV VITE_CLERK_PUBLISHABLE_KEY=$VITE_CLERK_PUBLISHABLE_KEY
ENV VITE_CLERK_FRONTEND_API=$VITE_CLERK_FRONTEND_API

COPY frontend/ ./
RUN npm run build

# -- Stage 2: Set up the Python Backend --
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for FAISS
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt ./

# CRITICAL: Install CPU-only torch to save massive space
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
# Copy built frontend from Stage 1
COPY --from=build-frontend /frontend/dist ./frontend/dist

# Set PYTHONPATH to include the backend directory
ENV PYTHONPATH=/app/backend

# Run the server
CMD ["python", "backend/app/main.py"]
