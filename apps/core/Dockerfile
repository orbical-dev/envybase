# apps/core/Dockerfile
FROM node:22-slim

WORKDIR /app

# Copy only the package files first for caching npm install
COPY package*.json ./

# Install dependencies (only production dependencies)
ENV NODE_ENV=production
RUN npm ci --only=production --no-progress --silent

# Now copy the rest of the app
COPY . .

# Build the Nuxt app
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", ".output/server/index.mjs"]
