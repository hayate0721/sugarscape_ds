# Makefile for Sugarscape Simulation Project

IMAGE_NAME=sugarscape
ECR_URL=851725177357.dkr.ecr.us-east-1.amazonaws.com/sugarscape

.PHONY: build push analyze clean

build:
	docker build -t $(IMAGE_NAME) .

push:
	docker tag $(IMAGE_NAME) $(ECR_URL):latest
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 851725177357.dkr.ecr.us-east-1.amazonaws.com
	docker push $(ECR_URL):latest

analyze:
	python3 data_analysis.py

clean:
	rm -rf results_from_s3 analysis_outputs all_records.csv summary_final_timesteps.csv
