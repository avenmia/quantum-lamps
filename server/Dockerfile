FROM node:12-alpine AS base

ARG VERSION=dev
ENV VERSION="${VERSION}"

WORKDIR /usr/src/app
COPY package.json package-lock.json ./

FROM base as build
RUN apk add --no-cache --update \
    python \
    make \
    g++
RUN npm ci
COPY . .
RUN  npm run build

FROM base as release
RUN npm install --production
COPY --from=build /usr/src/app/dist /usr/src/app/dist
EXPOSE  8080
CMD npm run start