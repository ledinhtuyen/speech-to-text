# Use NodeJS version 14
FROM node:23 AS builder

# Create directory
WORKDIR /app/frontend

# Copy package.json and package-lock.json
COPY frontend/package*.json ./

# Install all dependencies
RUN npm install

# Copy all files to container
COPY frontend/ .

# Build ReactJS
RUN npm run build

# Use Python version 3.10
FROM python:3.10

# Update pip
RUN pip install --upgrade pip

# Create directory
WORKDIR /app

# Copy requirements.txt
COPY backend/requirements.txt .

# Install all dependencies
RUN pip install -r requirements.txt

# Copy static files from ReactJS
COPY --from=builder /app/frontend/dist static

# Copy all files to container
COPY backend/ .

EXPOSE 443

# Run FastAPI
CMD ["hypercorn", "main:app", "--bind", "0.0.0.0:443"]