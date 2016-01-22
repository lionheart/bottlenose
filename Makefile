all: test publish

test:
	python setup.py test

publish:
	python setup.py sdist upload --sign
