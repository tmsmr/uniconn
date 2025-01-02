variable "prefix" {
  type = string
}

variable "name" {
  type = string
}

variable "type" {
  type = string

  validation {
    condition = contains(["unicorn", "controller"], var.type)
    error_message = "unicorn|controller"
  }
}

variable "x509_dir" {
  type = string
}
