FROM node:18-slim

WORKDIR /app

# Copy both package.json and package-lock.json for dependable npm install.
COPY package.json package-lock.json* ./
RUN npm install

COPY public ./public
COPY src ./src

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]