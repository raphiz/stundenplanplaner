.PHONY: build test

default: buildimage

buildimage:
	docker build -t raphiz/hsrplanner .

test:
	docker run -t --rm --name hsrplanner -v $(shell pwd):/src/ -p 4000:4000 raphiz/hsrplanner /bin/bash -c "/src/setup.py develop -N; py.test -s ${ARGS}; rm -Rf planner.egg-info"
