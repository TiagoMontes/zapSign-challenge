.PHONY: help env build up down ps logs web/sh db/sh db/psql bootstrap manage migrate createsuperuser collectstatic test

DEFAULT_GOAL := help

help:
	@echo "Useful targets:"
	@echo "  env              Copy .env.example to .env (if missing)"
	@echo "  build            Build images"
	@echo "  up               Start services (detached)"
	@echo "  down             Stop services"
	@echo "  ps               List services"
	@echo "  logs             Tail all logs"
	@echo "  web/sh           Open a shell in the web container"
	@echo "  db/sh            Open a shell in the db container"
	@echo "  db/psql          Open psql connected to the app database"
	@echo "  bootstrap        Run django-admin startproject (first time)"
	@echo "  manage cmd=...   Run django manage.py <cmd>"
	@echo "  migrate          Run database migrations"
	@echo "  createsuperuser  Create Django superuser"
	@echo "  test             Run Django tests"

env:
	@test -f .env || cp .env.example .env

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f

web/sh:
	docker compose exec web sh

db/sh:
	docker compose exec db sh

db/psql:
	docker compose exec db sh -lc 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

# Initialize a new Django project named 'config' in the current folder
bootstrap:
	docker compose run --rm web sh -lc 'django-admin startproject config .'

manage:
	docker compose exec web python manage.py $(cmd)

migrate:
	$(MAKE) manage cmd=migrate

createsuperuser:
	$(MAKE) manage cmd=createsuperuser

collectstatic:
	$(MAKE) manage cmd='collectstatic --noinput'

test:
	$(MAKE) manage cmd='test tests'
