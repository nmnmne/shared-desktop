# shared_desktop_frontend

docker build -t inteonmteca/shared_ui .
docker push inteonmteca/shared_ui

docker-compose -f docker-compose-frontend.yml down
docker pull inteonmteca/shared_ui:latest
docker-compose -f docker-compose-frontend.yml up -d

docker image ls
docker rmi c7cfd4952c79 de977e057e03
docker image prune

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
npx serve dist
```
