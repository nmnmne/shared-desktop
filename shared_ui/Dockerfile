# Используем официальный образ Node.js для сборки
FROM node:20 as build-stage

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Устанавливаем правильную версию esbuild
RUN npm install esbuild@0.25.0

# Копируем все файлы проекта
COPY . .

# Собираем проект
RUN npm run build

# Используем легковесный образ Nginx для запуска приложения
FROM nginx:alpine as production-stage

# Копируем собранные файлы из предыдущего этапа в Nginx
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Копируем конфигурацию Nginx (если нужно)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт 80
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
