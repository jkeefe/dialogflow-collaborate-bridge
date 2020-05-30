# Smarts API Lambda Starter

This is my template for spinning up a new lambda function using the Really Good Smarts infrastructure. It relies on the databases and other settings established in the [Smarts Infrastructure repo](https://github.com/jkeefe/smarts-infrasturcture).

## Starting a new project

- **Create a new repo from this template**: Click the "Use this template" button on the [Smarts API Lambda Starter repo](https://github.com/jkeefe/smarts-api-lambda-starter) Github page

- **Get your environment going**:
    - Initiate the environment with `pipenv install`
    - Get the required modules for the API: `pipenv install flask flask-lambda-python36`
    - Install the other packages you need, like `pipenv install jupyterlab requests pymysql sqlalchemy ...`
    - Make an `.env` file for secrets if necessary, copying from a previous project. Note that this is just for Jupyter. For the lambda function to work, secrets also need to be in `terraform.tfvars` (see below)
    - Run Jupyter with `pipenv run jupyter lab` 
    
- **Code your code!**
    - Build your code in a Jupyter notebook, using the `notebooks` folder
    - When you're done, be sure "run all cells" works as you like
    
- **Prep it as an api endpoint**
    - Export your finished code as a `.py` file (called a "script" in the notebook)
    - Use `lambda_function/app/api/endpoints/bird.py` as an example, putting your code in the `def handler():` function
    - Add the new route in `lambda_function/app/api/routes.py` following the bird example

- **Prep your deployment**:
    - In the `Makefile` change `put-repo-name-here` to the name of your repo
    - In `terraform/main.tf` change `put-repo-name-here` to the name of your repo
    - Create or copy a `terraform/terraform.tfvars` file for secrets. See the example if needed.
        - NOTE: If you don't need secrets ... rename `.terraform.tvars.example` to `.terraform.tvars` to keep things from breaking.
    - Initialize Terraform with `make init` (note that Docker must be running)
    - Create your layer file with `make layer`. This will zip your Python packages and put them on S3.
    
- **Deploy!**
    - Commit your code to git. Your working directory must be clean.
    - See what's going to happen with `make plan`
    - Deploy your code with `make do`
    
- **Debugging and revising**:
    - I test the function from the AWS console
    - Re-deploy as necessary, using the **Deploy** steps
    - If you change the Python packages, update the lambda layer using `make layer` and **Deploy**.
    - Adjust lambda memory & timeout in `lambda.tf` to taste.
    - Set up CloudWatch events to trigger the function
    
