# Use the official Node.js runtime as the base image
FROM node:18-alpine AS base

# Install pnpm
RUN npm install -g pnpm

# Set the working directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy the rest of the application
COPY . .

# Build the application
RUN pnpm build

# Production stage
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

# Install pnpm
RUN npm install -g pnpm

# Copy built application
COPY --from=base /app/.next ./.next
COPY --from=base /app/public ./public
COPY --from=base /app/package.json ./package.json
COPY --from=base /app/pnpm-lock.yaml ./pnpm-lock.yaml

# Install only production dependencies
RUN pnpm install --frozen-lockfile --prod

# Expose port 3000
EXPOSE 3000

# Start the application
CMD ["pnpm", "start"]