# Stage 1: Build React App
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

# Build with production mode
RUN npm run build

# Stage 2: Serve using Nginx Alpine (Lightweight standalone for frontends, if needed, but our compose will mount custom reverse proxy)
# We will use this simply config to serve the static assets immediately internally, and the primary proxy handles routing.
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
