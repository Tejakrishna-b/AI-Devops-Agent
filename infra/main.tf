# Terraform starter file
# Define your infrastructure resources here

terraform {
  required_version = ">= 1.0.0"
}

provider "azurerm" {
  features {}
}

# Example resource
resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "East US"
}
