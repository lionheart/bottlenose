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
all: clean test publish

clean:
	rm -rf dist/

test:
	python setup.py test

publish: clean
	python setup.py bdist_wheel --universal
	python3 setup.py bdist_wheel --universal
	gpg --detach-sign -a dist/*.whl
	twine upload dist/*

