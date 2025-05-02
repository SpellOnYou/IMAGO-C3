FROM node:20

WORKDIR /frontend

COPY package.json /frontend/
RUN npm install

COPY ./src /frontend/src
COPY ./public /frontend/public

CMD ["npm", "start"]
