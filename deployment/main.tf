data "aws_caller_identity" "current" {}

data "aws_iot_endpoint" "current" {}

resource "random_pet" "deployment_id" {
  length = 2
}

resource "aws_iot_policy_attachment" "uniconn_policy_attachment" {
  for_each = var.uniconns
  policy   = aws_iot_policy.uniconn_policy[each.key].name
  target   = aws_iot_certificate.uniconn_cert[each.key].arn
}

resource "aws_iot_thing_principal_attachment" "uniconn_principal_attachment" {
  for_each  = var.uniconns
  principal = aws_iot_certificate.uniconn_cert[each.key].arn
  thing     = aws_iot_thing.uniconn_thing[each.key].name
}

resource "local_file" "uniconn_config" {
  for_each = var.uniconns
  content = jsonencode({
    mqtt_endpoint   = data.aws_iot_endpoint.current.endpoint_address
    client_id       = random_uuid.uniconn_client_id[each.key].result
    my_topic        = "${each.key}-${random_pet.deployment_id.id}"
    broadcast_topic = random_pet.deployment_id.id
  })
  filename = "${path.module}/unicorns/tmp/${each.key}/config.json"
}

resource "archive_file" "uniconn_archive" {
  for_each   = var.uniconns
  type       = "zip"
  source_dir = "${path.module}/unicorns/tmp/${each.key}"
  excludes = [
    "*.pem"
  ]
  output_path = "${path.module}/unicorns/${each.key}.zip"
  depends_on = [
    null_resource.pem_to_der,
    local_file.uniconn_config
  ]
}
