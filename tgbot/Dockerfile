FROM node:22-alpine

WORKDIR /opt/app

COPY package*.json .

RUN npm ci

COPY ./src ./src
COPY ./tsconfig.json ./tsconfig.json
