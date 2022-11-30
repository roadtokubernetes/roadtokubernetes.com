vendor_files:
	rm -rf src/static/vendor
	mkdir -p src/static/vendor/dompurify/
	mkdir -p src/static/vendor/highlight/
	mkdir -p src/static/vendor/flowbite/
	mkdir -p src/static/vendor/showdown/
	mkdir -p src/static/vendor/htmx/
	curl -L https://unpkg.com/htmx.org@1.8.2 -o ./src/static/vendor/htmx/htmx.min.js
	cp node_modules/dompurify/dist/purify.min.js ./src/static/vendor/dompurify/purify.min.js
	curl https://unpkg.com/@highlightjs/cdn-assets@11.6.0/highlight.min.js -o src/static/vendor/highlight/highlight.min.js
	cp node_modules/highlight.js/styles/monokai-sublime.css ./src/static/vendor/highlight/monokai-sublime.min.css
	cp node_modules/flowbite/dist/flowbite.js ./src/static/vendor/flowbite/flowbite.js
	cp node_modules/showdown/dist/showdown.min.js ./src/static/vendor/showdown/showdown.min.js

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

rollout:
	kubectl rollout restart deployment/www-roadtokubernetes-com-deployment

# act  workflow_dispatch -W .github/workflows/build-container.yaml  --secret-file .secrets -v



# does not work locally
act_db_init_test:
	echo ".github/workflows/db-init-test.yaml will not run locally with act"
	act workflow_dispatch -W .github/workflows/db-init-test.yaml --secret-file .secrets 


# act workflow_dispatch -W .github/workflows/db-init-test.yaml --secret-file .secrets 
