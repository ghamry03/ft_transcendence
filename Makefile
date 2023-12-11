NAME			=	ft_transcendence

DOCKER_CMD		=	docker compose -f $(COMPOSE_PATH) -p $(NAME)

COMPOSE_PATH	=	./docker_srcs/docker-compose.yml

$(NAME)			:	build up

all				:	$(NAME)

build			:
					mkdir -p ./srcs/postgres/data
					$(DOCKER_CMD) build

up				:
					$(DOCKER_CMD) up -d

down			:
					$(DOCKER_CMD) down

server			:
					$(DOCKER_CMD) up -d --no-deps --build server

main			:
					$(DOCKER_CMD) up -d --no-deps --build main_app

auth			:
					$(DOCKER_CMD) up -d --no-deps --build auth_app

postgres		:
					$(DOCKER_CMD) up -d --no-deps --build postgres

server-sh		:
					$(DOCKER_CMD) exec -it server /bin/bash

main-sh		:
					$(DOCKER_CMD) exec -it main_app /bin/bash

auth-sh		:
					$(DOCKER_CMD) exec -it auth_app /bin/bash

db-sh		:
					$(DOCKER_CMD) exec -it postgres /bin/bash

ps				:
					$(DOCKER_CMD) ps

logs			:
					$(DOCKER_CMD) logs

clean			:	down

fclean			:
					$(DOCKER_CMD) down -v --rmi all

re				: fclean all

.PHONY			:	$(NAME) all build up down clean fclean re	\
					server main_app auth_app postgres			\
					server-sh main-sh auth-sh postgres-sh
