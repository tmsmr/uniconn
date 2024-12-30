resource "random_uuid" "uniconn_client_id" {
  for_each = var.uniconns
}

resource "aws_iot_thing" "uniconn_thing" {
  for_each = var.uniconns
  name     = "uniconn-${each.key}-${random_pet.deployment_id.id}"
}
