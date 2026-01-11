FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY . .

# Create .env file if it doesn't exist
RUN if [ ! -f .env ]; then \
      echo "PORT=3001" >> .env && \
      echo "JWT_SECRET=super-secret-key-for-development-only" >> .env && \
      echo "MONGODB_URI=mongodb://mongo:27017/chatapp-users" >> .env; \
    fi

EXPOSE 3001

CMD ["npm", "start"]