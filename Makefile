.PHONY: build test

run_in_docker = docker run -t -i --rm --name hsrplanner -v $(shell pwd):/src/ -p 4000:4000 raphiz/hsrplanner /bin/bash -c

default: buildimage

buildimage:
	docker build -t raphiz/hsrplanner .

test:
	$(run_in_docker) "/src/setup.py develop -N;py.test ${ARGS};rm -Rf planner.egg-info"

demo:
	$(run_in_docker) "/src/setup.py develop -N;python demo.py;rm -Rf planner.egg-info"

python_shell:
	$(run_in_docker) "python"
