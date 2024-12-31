variable "uniconns" {
  type = map(object({
    ssid    = string
    psk     = string
    country = string
    type    = string
  }))
}

variable "aws_region" {
  type = string
}
