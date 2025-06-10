# dashboard/Dockerfile

########################
# 1) Build the SPA
########################
FROM node:18-alpine AS builder
WORKDIR /app

# Copy package definitions and install
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source & build
COPY . .
RUN npm run build      # outputs "./dist" per vite.config.js

########################
# 2) Serve with Nginx
########################
FROM nginx:stable-alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Add our custom config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built SPA from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s \
  CMD wget -q --spider http://localhost/health || exit 1
