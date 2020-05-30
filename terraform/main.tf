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
    key    = "put-repo-name-here"  ## change this to repo name
    region = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region     = "us-east-1"
}
