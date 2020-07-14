variable "repo_name" {}
variable "version_key" {}
variable "version_bucket" {}

output "lambda_function_name" { 
    value = aws_lambda_function.project_lambda.function_name
}

### If you're not using the database infrastructure,
### Comment ou these lines:
variable "db_user" {
    type = string
}

variable "db_name" {
    type = string
}

variable "db_password" {
    type = string
}

variable "slack_url" {
    type = string
}

variable "GSPREAD_PANDAS_CONFIG_DIR" {
    type = string
}