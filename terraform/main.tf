data "terraform_remote_state" "aws" {
  backend = "s3"
  workspace = "default"
  config = {
    bucket = "pp-aws-terraform"  ## NOTE! Bucket versioning must be enabled
    key    = "infra-dialogflow-collaborate-bridge"
    region = "us-east-1"
    dynamodb_table = "pp-aws-terraform-locks2"  ## Must use primarykey named LockID
  }
}

terraform {
  backend "s3" {
    bucket = "pp-aws-terraform"  ## NOTE! Bucket versioning must be enabled
    key    = "app-dialogflow-collaborate-bridge"
    region = "us-east-1"
    dynamodb_table = "pp-aws-terraform-locks2"  ## Must use primarykey named LockID
  }
}

provider "aws" {
  region     = "us-east-1"
}
