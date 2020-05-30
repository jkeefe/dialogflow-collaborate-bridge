resource "aws_lambda_function" "project_lambda" {
  function_name    = var.repo_name
  role             = data.terraform_remote_state.aws.outputs.lambda_role_arn
  handler          = "run_lambda.http_server"
  runtime          = "python3.7"
  s3_bucket        = var.version_bucket
  s3_key           = var.version_key    
  memory_size      = 256
  timeout          = 30
  publish          = true
  layers           = [aws_lambda_layer_version.layer.arn]
  vpc_config  {
    security_group_ids = [data.terraform_remote_state.aws.outputs.aws_security_group_for_lambdas]
    subnet_ids = data.terraform_remote_state.aws.outputs.private_subnets
  }

  ## Environment variables are loaded from the
  ## terraform.tfvars file, which is not checked into github
  ## see terraform.tfvars.example as an example
  environment {
    variables = {
      version_key      = var.version_key
      RDS_ENDPOINT     = data.terraform_remote_state.aws.outputs.public_rds_endpoint   
      DBHOST           = data.terraform_remote_state.aws.outputs.public_rds_endpoint
      DBNAME           = var.db_name
      DBUSER           = var.db_user
      DBPASSWORD       = var.db_password
      SLACK_URL        = var.slack_url
    }
  }
}

resource "aws_lambda_alias" "prod" {
  name             = "prod"
  description      = "prod alias"
  function_name    = aws_lambda_function.project_lambda.arn
  function_version = aws_lambda_function.project_lambda.version
}


### Permissions for API Gateway
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.project_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}



### Lambda layers ###
# ... for uploading our python packages 

# This establishes a data link to the .zip file with the latest packages.
# It's created (and versioned) with 'make layer'
data "aws_s3_bucket_object" "layer_file" {
  bucket = var.version_bucket
  key    = "${var.repo_name}/project_layer_package.zip"
}

# This creates and updates the lambda layer for this repo
resource "aws_lambda_layer_version" "layer" {
  s3_bucket           = data.aws_s3_bucket_object.layer_file.bucket
  s3_key              = data.aws_s3_bucket_object.layer_file.key
  layer_name          = "${var.repo_name}-layer"
  s3_object_version   = data.aws_s3_bucket_object.layer_file.version_id
  compatible_runtimes = ["python3.7"]
}

