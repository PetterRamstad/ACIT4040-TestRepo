FROM node:22-alpine AS build
WORKDIR /app
COPY apps/frontend/package*.json ./
RUN npm install
COPY apps/frontend ./
RUN npm run build
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
