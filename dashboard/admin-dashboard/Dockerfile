# ---------- build stage ----------
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build         # writes to /app/dist
# ---------- runtime stage ----------
FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# tiniest config – just serve static files
