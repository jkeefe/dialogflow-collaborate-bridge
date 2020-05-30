data "terraform_remote_state" "aws" {
  backend = "s3"
  workspace = "default"
  config = {
    bucket = "smarts-terraform"
    key    = "infrastructure"
    region = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}

terraform {
  backend "s3" {
    bucket = "smarts-terraform"
    key    = "dialogflow-collaborate-bridge"  ## change this to repo name
    region = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region     = "us-east-1"
}
