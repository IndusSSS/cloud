FROM node:20-bullseye AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-distutils make g++ build-essential \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && python3 -m ensurepip --upgrade \
    && rm -rf /var/lib/apt/lists/*
COPY package.json tsconfig.json ./
RUN npm install
COPY src ./src
RUN npm run build

FROM node:20-bullseye
WORKDIR /app
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-distutils make g++ build-essential \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && python3 -m ensurepip --upgrade \
    && rm -rf /var/lib/apt/lists/*
COPY package.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
ENV NODE_ENV=production
CMD ["node", "dist/index.js"]
