# syntax=docker/dockerfile:1 

FROM node:18-bookworm as base
WORKDIR /app

COPY package-lock.json package.json ./

RUN apt-get update \
  && apt-get install --no-install-recommends -y libopencv-dev

RUN npm ci \
  && npx build-opencv --nobuild rebuild

COPY . .
RUN npm run build

EXPOSE 5000
CMD ["npm", "run", "start"]
