DEV_IMAGE_NAME = burenotti/bruhsty-dev
DEV_IMAGE_TAG = latest

PROD_IMAGE_NAME = burenotti/bruhsty
PROD_IMAGE_TAG = latest

_docker_build:
	docker bulid -f Dockerfile -t $(PROD_IMAGE_NAME):$(PROD_IMAGE_TAG) .

_docker_build_dev:
	docker build -f Dockerfile.dev -t $(DEV_IMAGE_NAME):$(DEV_IMAGE_TAG) .

test:
	docker compose -f docker-compose.test.yaml run --rm -it test


build:
	docker compose -f docker-compose.yaml run build bot

up:
	docker compose -f docker-compose.yaml up -d
