NAME			=	ft_transcendence

DOCKER_CMD		=	docker compose -f $(COMPOSE_PATH) -p $(NAME)

prod			=	0

ifeq ($(prod), 1)
	COMPOSE_PATH	=	./docker_srcs/docker-compose.prod.yml
else
	COMPOSE_PATH	=	./docker_srcs/docker-compose.yml
endif

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
					$(DOCKER_CMD) up -d --no-deps --build mainapp

user			:
					$(DOCKER_CMD) up -d --no-deps --build userapp

postgres		:
					$(DOCKER_CMD) up -d --no-deps --build postgres

server-sh		:
					$(DOCKER_CMD) exec -it server /bin/bash

main-sh		:
					$(DOCKER_CMD) exec -it mainapp /bin/bash

user-sh		:
					$(DOCKER_CMD) exec -it userapp /bin/bash
friends-sh		:
					$(DOCKER_CMD) exec -it friendsapp /bin/bash

game-sh		:
					$(DOCKER_CMD) exec -it gameapp /bin/bash

tour-sh		:
					$(DOCKER_CMD) exec -it tourapp /bin/bash

db-sh		:
					$(DOCKER_CMD) exec -it postgres /bin/bash

main-logs		:
					docker logs -f mainapp

user-logs		:
					docker logs -f userapp

game-logs		:
					docker logs -f gameapp

tour-logs		:
					docker logs -f tourapp

psql		:
					$(DOCKER_CMD) exec postgres psql --username=postgres --dbname=usermanagement

ps				:
					$(DOCKER_CMD) ps

logs			:
					$(DOCKER_CMD) logs -f

clean			:	down

fclean			:
					$(DOCKER_CMD) down -v --rmi all
					rm -rf srcs/postgres/data
					rm -rf srcs/friends_app/friends_api/migrations/
					rm -rf srcs/friends_app/friends_api/__pycache__/
					rm -rf srcs/user_app/user_api/migrations/
					rm -rf srcs/user_app/user_api/__pycache__/

re				: fclean all

.PHONY			:	$(NAME) all build up down clean fclean re	\
					server mainapp userapp postgres			\
					server-sh main-sh user-sh postgres-sh
