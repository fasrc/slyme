mocked:
	python test_util.py
	python test_job_queries_mock.py

live:
	test `hostname -f` = slurm-test.rc.fas.harvard.edu || $(error You must be at FASRC and on slurm-test to run the live tests.)
	python test_job_queries_live.py
	python test_job_workflow_live.py

all: mocked live
