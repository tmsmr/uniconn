data "aws_caller_identity" "current" {}

data "aws_iot_endpoint" "current" {
  endpoint_type = "iot:Data-ATS"
}

resource "random_pet" "deployment_id" {
  length = 2
}

resource "aws_iot_policy_attachment" "uniconn_policy_attachment" {
  for_each = var.uniconns
  policy   = aws_iot_policy.uniconn_policy[each.key].name
  target   = aws_iot_certificate.uniconn_cert[each.key].arn
}

resource "aws_iot_policy_attachment" "client_policy_attachment" {
  for_each = var.clients
  policy   = aws_iot_policy.client_policy[each.key].name
  target   = aws_iot_certificate.client_cert[each.key].arn
}

resource "aws_iot_thing_principal_attachment" "uniconn_principal_attachment" {
  for_each  = var.uniconns
  principal = aws_iot_certificate.uniconn_cert[each.key].arn
  thing     = aws_iot_thing.uniconn_thing[each.key].name
}

resource "aws_iot_thing_principal_attachment" "client_principal_attachment" {
  for_each  = var.clients
  principal = aws_iot_certificate.client_cert[each.key].arn
  thing     = aws_iot_thing.client_thing[each.key].name
}

resource "local_file" "uniconn_config" {
  for_each = var.uniconns
  content = jsonencode({
    mqtt_host       = data.aws_iot_endpoint.current.endpoint_address
    mqtt_port       = 8883
    client_id       = random_uuid.uniconn_client_id[each.key].result
    uniconn_topic   = "${random_pet.deployment_id.id}/${each.key}/pixels"
    broadcast_topic = "${random_pet.deployment_id.id}/all/pixels"
    uniconn_type    = each.value.type
    wifi_ssid       = each.value.ssid
    wifi_psk        = each.value.psk
    wifi_country    = each.value.country
  })
  filename = "${path.module}/unicorns/tmp/${each.key}/config.json"
}

resource "local_file" "client_config" {
  for_each = var.clients
  content = jsonencode({
    mqtt_host  = data.aws_iot_endpoint.current.endpoint_address
    mqtt_port  = 8883
    client_id  = random_uuid.client_client_id[each.key].result
    uniconns   = [
      for name, uniconn in var.uniconns : {
        name  = name
        type  = uniconn.type
        topic = "${random_pet.deployment_id.id}/${name}/pixels"
      }
    ]
  })
  filename = "${path.module}/clients/tmp/${each.key}/config.json"
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
  provisioner "local-exec" {
    when    = destroy
    command = "rm ${path.module}/unicorns/${each.key}.zip"
  }
}

resource "archive_file" "client_archive" {
  for_each   = var.clients
  type       = "zip"
  source_dir = "${path.module}/clients/tmp/${each.key}"
  output_path = "${path.module}/clients/${each.key}.zip"
  depends_on = [
    local_file.client_cert_pem,
    local_file.client_key_pem,
    local_file.aws_root_ca_pem_clients,
    local_file.client_config
  ]
  provisioner "local-exec" {
    when    = destroy
    command = "rm ${path.module}/clients/${each.key}.zip"
  }
}
