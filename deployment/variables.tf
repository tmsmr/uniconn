variable "uniconns" {
  type = map(object({
    ssid = string
    psk  = string
  }))
}

variable "aws_region" {
  type = string
}
