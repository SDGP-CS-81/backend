# syntax=docker/dockerfile:1 

FROM node:18-alpine as base
WORKDIR /app

COPY package-lock.json package.json ./

RUN apk update \
  && apk add

RUN npm ci 

COPY . .
RUN npm run build

EXPOSE 5000
CMD ["npm", "run", "start"]
