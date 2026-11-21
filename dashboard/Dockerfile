FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --omit=dev

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production PORT=3000
COPY --from=build /app/build ./build
COPY --from=build /app/node_modules ./node_modules
COPY package.json .
EXPOSE 3000
# Variables à fournir au runtime : BACKEND_SERVICE_URL, ORIGIN, GOOGLE_*, AUTH_COOKIE_SECURE…
CMD ["node", "build"]
