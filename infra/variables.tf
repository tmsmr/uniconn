variable "unicorns" {
  type = map(object({
    unicorn_type = string
    wifi_ssid    = string
    wifi_psk     = string
    wifi_country = string
  }))
}

variable "controllers" {
  type = set(string)
}
