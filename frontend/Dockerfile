FROM node:18-alpine3.14


# Create app directory
WORKDIR /app
RUN npm install -g react-scripts

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json /app/
RUN npm install

# If you are building your code for production
# RUN npm ci --only=production
EXPOSE 80
EXPOSE 3000

# Bundle app source
COPY . /app/

CMD [ "npm", "start" ]
