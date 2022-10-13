vendor_files:
	rm -rf src/static/vendor
	mkdir -p src/static/vendor/dompurify/
	mkdir -p src/static/vendor/highlight/
	mkdir -p src/static/vendor/flowbite/
	mkdir -p src/static/vendor/showdown/
	cp -R node_modules/dompurify/dist/ ./src/static/vendor/dompurify/
	curl https://unpkg.com/@highlightjs/cdn-assets@11.6.0/highlight.min.js -o src/static/vendor/highlight/highlight.min.js
	cp node_modules/highlight.js/styles/monokai-sublime.css ./src/static/vendor/highlight/monokai-sublime.min.css
	cp -R node_modules/flowbite/dist/ ./src/static/vendor/flowbite/
	cp -R node_modules/showdown/dist/ ./src/static/vendor/showdown/

tailwind_watch:
	npx tailwindcss -i ./src/static/src/tailwind-input.css -o ./src/static/src/tailwind-output.css --watch

docker_build:
	docker build -t roadtokubernetes.com -f Dockerfile .

docker_run:
	docker run -p 8080:8080 --network roadtokubernetescom_network --env-file ./src/stage.env roadtokubernetes.com

docker_stop:
	docker stop $$(docker ps -q --filter ancestor=roadtokubernetes.com)

docker_shell:
	docker exec -it $$(docker ps -q --filter ancestor=roadtokubernetes.com) /bin/bash

dc_up:
	docker compose -f docker-compose.dev.yaml up -d

dc_down:
	docker compose -f docker-compose.dev.yaml down 

dc_clear:
	docker compose -f docker-compose.dev.yaml  down -v

runserver:
	python src/manage.py runserver

k8s_verify:
	act workflow_dispatch -W .github/workflows/k8s-verify.yaml  --secret-file .secrets


k8s_apply:
	act workflow_dispatch -W .github/workflows/k8s-apply.yaml  --secret-file .secrets


act_build_container:
	act workflow_dispatch -W .github/workflows/build-container.yaml --secret-file .secrets -v


# act  workflow_dispatch -W .github/workflows/build-container.yaml  --secret-file .secrets -v
