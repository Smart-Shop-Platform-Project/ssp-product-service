variable "aws_region" { type = string; default = "us-east-1" }
variable "environment" { type = string }
variable "container_image" { type = string; default = "placeholder" }

variable "mongo_uri_param_name" {
  type        = string
  description = "The name of the SSM parameter for the MongoDB connection string."
  default     = "ssp/product/mongo_uri"
}
