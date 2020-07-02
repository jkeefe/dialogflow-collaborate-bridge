repo_name = propublica-dialogflow-collaborate-bridge
version_head = $(shell git rev-parse --short HEAD)
version_bucket = pp-lambda-zips-east1

tf = docker run \
	-v ${HOME}/.aws:/root/.aws \
	-v $(shell pwd)/terraform/\:/app/ \
	-e TF_VAR_version_key=$(repo_name)/$(version_head).zip \
	-e TF_VAR_version_bucket=$(version_bucket) \
	-e TF_VAR_repo_name=$(repo_name) \
	-e AWS_PROFILE=${AWS_PROFILE} \
	-w /app \
	hashicorp/terraform:0.12.21

init:
	@$(tf) init -reconfigure

plan: init
	@$(tf) plan

apply: check-s3 plan
	@$(tf) apply -auto-approve

show: init
	@$(tf) show

check-s3:
	@echo "-- Checking S3 --"
	@$(tools) aws s3api head-object --bucket ${version_bucket} --key $(repo_name)/$(version_head).zip || /bin/bash -c "echo -e \"\n\033[0;31mTerraform publishes a lambda function from S3 based on the Git SHA. Run 'make zip' or 'make do' to upload a new object to S3.\033[0m\n\" && exit 1"

zip:
	git diff --quiet . # Working directory must be clean
	cd lambda_function; zip -9 -qr $(version_head).zip * \
		--exclude ./*.pyc
	cd lambda_function; aws s3 cp $(version_head).zip s3://${version_bucket}/$(repo_name)/$(version_head).zip
	cd lambda_function; rm *.zip

layer:
	mkdir -p temp_deploy/python/lib
	@echo "`tput bold`\nCopying all the packages from .venv into a temp directory ...`tput sgr0`"
	cp -r $(shell pipenv --venv)/lib/* temp_deploy/python/lib
	@echo "`tput bold`\nZipping 'em up ...`tput sgr0`"
	cd temp_deploy; zip -9 -qr project_layer_package.zip *
	@echo "`tput bold`\nSending to S3 ...`tput sgr0`"
	cd temp_deploy; aws s3 cp project_layer_package.zip s3://${version_bucket}/$(repo_name)/project_layer_package.zip
	@echo "`tput bold`\nCleaning up ...`tput sgr0`"
	rm -rf temp_deploy
	@echo "`tput bold`\nDone! If you update your packages, you'll need to run 'make layer' again.\n`tput sgr0`"

do: zip apply
