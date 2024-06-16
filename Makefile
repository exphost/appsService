TAG = latest
APP = $(shell basename $(CURDIR))
build:
	docker build -t $(APP):$(TAG) .

run:
	docker run  --rm -e FLASK_ENV=development -p 5000:5000 -it $(APP):$(TAG)

test: build
	docker run  --rm -e FLASK_ENV=development -p 5000:5000 -it $(APP):$(TAG) pytest --cov --cov-report=term --cov=report=xml  --cov-report term-missing -vv
test-fast:
	docker run  --rm -e FLASK_ENV=development -v $(shell pwd)/app:/app -p 5001:5000 -it $(APP):$(TAG) pytest --cov --cov-report=term --cov=report=xml  --cov-report term-missing -vv 
lint:
	docker run  --rm -e FLASK_ENV=development -p 5000:5000 -it $(APP):$(TAG) flake8
