NAME			=	ft_transcendence

DOCKER_CMD		=	docker compose -f $(COMPOSE_PATH) -p $(NAME)

COMPOSE_PATH	=	./srcs/docker-compose.yml

$(NAME)			:	build up

all				:	$(NAME)

build			:
					$(DOCKER_CMD) build

up				:
					$(DOCKER_CMD) up -d

down			:
					$(DOCKER_CMD) down

nginx			:
					$(DOCKER_CMD) up -d --no-deps --build nginx

django			:
					$(DOCKER_CMD) up -d --no-deps --build django

postgres		:
					$(DOCKER_CMD) up -d --no-deps --build postgres

nginx-sh		:
					$(DOCKER_CMD) exec -it nginx /bin/bash

django-sh		:
					$(DOCKER_CMD) exec -it django /bin/bash

postgres-sh		:
					$(DOCKER_CMD) exec -it postgres /bin/bash

ps				:

logs			:

cache-clear		:

clean			:

fclean			:

re				:

.PHONY			:	$(NAME) all backend database server clean fclean re
