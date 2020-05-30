# Process notes

These are notes I write along the way. They may contain useful information and dead ends, and shouldn't be considered formal documentation.

## Plan

### Terraform

- Establish a project directory structure
- Establish a super-simple python file
- Setup Terraform Makefile (with no complicated subnets, etc)
- Initialize and deploy the simple python file

### AWS Console

- Build a Pandas lambda layer
- Upload that layer to the lambda, probably with the console
- Turn on the sci/pi layer
- Look into (but maybe not do) how to do that in Terraform
- Put environment keys in via console
- But also make sure to exclude those from the lifetime notes in Terraform

### Python notebook

- Check the power outage api every 15 mins
- Store to a table

- National weather service
    - figure out the xml thang
    - be sure to check the start / end times for that
    - store any counties with warnings

- Do a query … any current county outages that fall outside a warning window (or were in a warning situation in the past X amount of time … maybe today?)
- Slack the counties that are out, with the numbers
- Maybe even a map :-)

## Setup

- Adjusted the terraform files to allow public access to the database
    - set `publicly_accessible = true` for the cluster instance in `rds.tf`
    - opened an ingress from my house in  `security_group.tf`
    - NOTE: if it doesn't work, try making `aws_db_subnet_group` in `rds.tf` public instead of private
- Renamed lambda project using a variable :-)
    - **For future projects: 
        - change the repo_name atop the Makefile** to match the repo name
        - **change the name of the S3 key** in `main.tf`
- Established the right aws profile:

```
export AWS_PROFILE=johnkeefe-newspicks
```

- Did `make init`
- Did `make plan`

### API Setup

Following [really good instructions from Andrew Griffiths](https://andrewgriffithsonline.com/blog/180412-deploy-flask-api-any-serverless-cloud-platform/). 

Modifications:
- Needed to make the `run_lambda.py` file
- Needed to update the `api/__init__.py` file
- To test locally:

```
pipenv shell
cd lambda_function
FLASK_DEBUG=1 FLASK_APP=run.py flask run
```

In a browser, try `http://localhost:5000/` and `http://localhost:5000/artists`

