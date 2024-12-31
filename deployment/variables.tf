variable "uniconns" {
  type = map(object({
    ssid = string
    psk  = string
    type = string
  }))
}

variable "aws_region" {
  type = string
}
