# Frontend Dockerfile for Ops Phase 0.1
FROM node:22-slim

WORKDIR /app

# Copy package files first (better caching)
COPY ../digi-tax-frontend/package.json ../digi-tax-frontend/.npmrc ./

# Install pnpm globally (simpler approach)
RUN npm install -g pnpm

# Install dependencies using pnpm
RUN pnpm install

# Copy source files
COPY ../digi-tax-frontend/. .

# Expose port for dev server
EXPOSE 9000

# Default command - start dev server
CMD ["pnpm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "9000"]
