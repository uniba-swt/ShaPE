
test:
	python -m pytest --verbose tests

unit:
	python -m pytest --verbose tests/unit

integration:
	python -m pytest --verbose tests/integration

integration-match:
	python -m pytest --verbose tests/integration/test_match.py

integration-learn:
	python -m pytest --verbose tests/integration/test_learn.py

integration-composition:
	python -m pytest --verbose tests/integration/test_composition.py

integration-verifast:
	python -m pytest --verbose tests/integration/test_verifast.py


docker-build:
	docker build . -t "jboockmann.shape"

docker-test: docker-build
	docker run -it jboockmann.shape bash -c "make test"

docker-bash: docker-build
	docker run -it jboockmann.shape bash