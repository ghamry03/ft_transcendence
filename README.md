# ft_transcendence

Below is an example of the folder and file logic used:

	project_root/
	├── app1/
	│   ├── templates/
	│   │   ├── app1/
	│   │   │   ├── template1.html
	│   │   ├── static/
	│   │   │   ├── 404.html
	│   │   │   ├── 500.html

------------------------------------------------------------
Below is the folder and file logic implemented:
------------------------------------------------------------
	main_app/
	├── app1/
	│   ├── templates/
	│   │   ├── app1/
	│   │   │   ├── template1.html
	│   │   ├── static/
	│   │   │   ├── 404.html
	│   │   │   ├── 500.html
	|
	docker_srcs/
	├── django
	│  ├── Dockerfile
	│  ├── requirements.txt
	│  └── srcs
	│    └── test
	├── docker-compose.yml 										// define volumes to be main directories
	├── env.example
	├── nginx
	│  └── Dockerfile
	└── postgres
	  └── Dockerfile
	|
	Makefile