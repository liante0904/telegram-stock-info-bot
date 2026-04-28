COMPOSE := docker compose

.PHONY: up down restart logs ps

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

logs-bot:
	$(COMPOSE) logs -f telegram-bot

logs-worker:
	$(COMPOSE) logs -f reporter-worker

ps:
	$(COMPOSE) ps
