FROM node:20-bullseye AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y python3 make g++ \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*
COPY package.json tsconfig.json ./
RUN npm install
COPY src ./src
RUN npm run build

FROM node:20-bullseye
WORKDIR /app
RUN apt-get update && apt-get install -y python3 make g++ \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/dist ./dist
COPY package.json ./
RUN npm install --omit=dev
ENV NODE_ENV=production
CMD ["node", "dist/index.js"]
