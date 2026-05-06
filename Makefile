.PHONY: reproduce test report demo portfolio-demo

reproduce:
	PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir . --top-k 5

test:
	python3 -m pytest

report:
	PYTHONPATH=src python3 -m heuristic_discovery report --output-dir . --top-k 5

demo:
	PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-demo --top-k 3

portfolio-demo:
	PYTHONPATH=src python3 -m heuristic_discovery reproduce --profile local_demo --output-dir /tmp/o2-portfolio-demo --top-k 3
