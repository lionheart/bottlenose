# Copyright 2014-2018 Lionheart Software LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Usage: make VERSION=0.1.2

METADATA_FILE := $(shell find . -name "metadata.py" -depth 2)

all: clean test publish

clean:
	rm -rf dist/

test:
	python setup.py test
	python3 setup.py test

update_readme:
	pandoc --from=markdown --to=rst --output=README.rst README.md
	-git reset
	-git add README.rst
	-git commit -m "update README.rst from README.md"

update_version:
	sed -i "" "s/\(__version__[ ]*=\).*/\1 \"$(VERSION)\"/g" $(METADATA_FILE)
	git add .
	# - ignores errors in this command
	-git commit -m "bump version to $(VERSION)"
	# Delete tag if already exists
	-git tag -d $(VERSION)
	-git push origin master :$(VERSION)
	git tag $(VERSION)
	git push origin master
	git push --tags

publish: clean update_readme update_version
	python setup.py bdist_wheel --universal
	python3 setup.py bdist_wheel --universal
	gpg --detach-sign -a dist/*.whl
	twine upload dist/*

