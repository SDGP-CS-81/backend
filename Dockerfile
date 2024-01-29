# syntax=docker/dockerfile:1 

FROM node:18-bookworm as base
WORKDIR /app
COPY . .

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libopencv-dev

RUN npm ci
RUN npx build-opencv --nobuild rebuild
RUN npm run build

EXPOSE 5000
CMD npm run start
