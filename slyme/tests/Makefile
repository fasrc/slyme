mocked:
	python test_util.py
	python test_job_queries_mock.py

live:
ifneq ($(HOSTNAME), slurm-test.rc.fas.harvard.edu)
	$(error you must be at FASRC and on slurm-test to run the live tests)
else
	python test_job_queries_live.py
	python test_job_workflow_live.py
endif

all: mocked live
