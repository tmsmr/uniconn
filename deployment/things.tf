resource "random_uuid" "uniconn_client_id" {
  for_each = var.uniconns
}

resource "random_uuid" "client_client_id" {
  for_each = var.clients
}

resource "aws_iot_thing" "uniconn_thing" {
  for_each = var.uniconns
  name     = "uniconn-${each.key}-${random_pet.deployment_id.id}"
}

resource "aws_iot_thing" "client_thing" {
  for_each = var.clients
  name     = "client-${each.key}-${random_pet.deployment_id.id}"
}
