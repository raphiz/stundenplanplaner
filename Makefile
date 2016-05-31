.PHONY: build test

run_in_docker = docker run -t -i --rm --name hsrplanner -v $(shell pwd):/src/ raphiz/hsrplanner /bin/bash -c

default: buildimage

buildimage:
	docker build -t raphiz/hsrplanner .

test:
	$(run_in_docker) "/src/setup.py develop -N;py.test ${ARGS};rm -Rf planner.egg-info"

demo_timetables:
	$(run_in_docker) "/src/setup.py develop -N;python demos/generate_timetables.py;rm -Rf planner.egg-info"

demo_friends:
	$(run_in_docker) "/src/setup.py develop -N;python demos/friends.py;rm -Rf planner.egg-info"


python_shell:
	$(run_in_docker) "python"
