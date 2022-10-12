# Getting the Vendor Assets (JavaScript & CSS)

To get and use all vendor files, check `package.json` and `Makefile`:

To install required vendor items:
```
npm install
```

To move vendor files: 
```
make vendor_files
```

To monitor tailwind changes:

```
make tailwind_watch
```



## Tailwind
```
npm install tailwindcss --save-dev
```
We use tailwind to produce `src/static/src/tailwind-output.css` from `src/static/src/tailwind-input.css` with the following command:

```
npx tailwindcss -i ./src/static/src/tailwind-input.css -o ./src/static/src/tailwind-output.css
```



## flowbite

```
npm install flowbite --save-dev

cp -R node_modules/flowbite/dist/ ./src/static/js/vendor/flowbite/
```

## Highlight.js
Download a from CDN and package on https://highlightjs.org/download/ and unzip it
```
curl https://unpkg.com/@highlightjs/cdn-assets@11.6.0/highlight.min.js -o src/static/js/vendor/highlight/highlight.min.js
```

Get the styles directly from the package:
```
npm install highlight.js --save-dev
cp node_modules/highlight.js/styles/monokai-sublime.css ./src/static/js/vendor/highlight/monokai-sublime.min.css
```

## Showdown.js
```
npm install showdown --save-dev

cp -R node_modules/showdown/dist/ ./src/static/js/vendor/showdown/
```


## DomPurify
https://github.com/cure53/DOMPurify

```
npm install dompurify --save-dev
cp -R node_modules/dompurify/dist/ ./src/static/js/vendor/dompurify/
```