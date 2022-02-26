start-emulators:
	docker-compose up -d

stop-emulators:
	docker-compose down

restart-emulators: stop-emulators start-emulators

test-all: test-lib

test-lib:
	cd packages/lib; jest

deps:
	yarn

build: deps
	yarn run lerna run build
	
lint: lint-prettier lint-eslint lint-markdown

lint-prettier:
	yarn run prettier -c "**/*.{js,jsx,ts,tsx,yml,yaml.md}"

lint-eslint:
	yarn run eslint . --ext .js,.jsx,.ts,.tsx

lint-markdown:
	yarn run markdownlint-cli2 *.md
