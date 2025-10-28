# VisPile interface

Our interface is built using Vue.js to compile native HTML/CSS/JavaScript. We style the interface using the Vuetify framework plugin. We build the visualizations using D3.js.

If you want to read more, check out these links:

- [Vue.js](https://vuejs.org/guide/introduction.html)
- [Vuetify](https://vuetifyjs.com/en/introduction/why-vuetify/)
- [D3.js](https://d3js.org/what-is-d3)

## Setup

Before you begin:

- Install Node.js `>= v22.x` and npm `>= v11.x` by visiting ([latest release](https://nodejs.org/en/))

First, install dependencies:

```bash
npm install
```

Then, run VisPile:

```bash
npm run dev
```

Navigate to [localhost:3000](http://localhost:3000/). You should see VisPile running in your browser :)

## Build

If you want to generate the native HTML/CSS/JavaScript files to host on your own server, first run:

```bash
npm run build
```

Then navigate to [dist](./dist/). You will find the compiled HTML/CSS/JavaScript. You can then copy and paste these files into your own web server!

### Changing the endpoint

You can configure the endpoint in [vite.config.js](./vite.config.js)

Add the following option to [vite.config.js](./vite.config.js) to match whatever sub-directory (i.e., URL path) the app will be hosted in:

```js
base: "/path/to/vispile",
```

For example, with the above, the URL will auto-correct to <http://localhost:3000/path/to/vispile>

NOTE: The files will expect that they are hosted at the endpoint from above (e.g., <https://domain.com/path/to/vispile>)

## Libraries

- D3.js `v7.9.x` [link](https://github.com/d3/d3)
- VueUse `v13.x.x` [link](https://vueuse.org/guide/)
