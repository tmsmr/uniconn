resource "aws_iot_certificate" "uniconn_cert" {
  for_each = var.uniconns
  active   = true
}

resource "local_file" "uniconn_cert_pem" {
  for_each = var.uniconns
  content  = aws_iot_certificate.uniconn_cert[each.key].certificate_pem
  filename = "${path.module}/unicorns/tmp/${each.key}/x509/cert.pem"
}

resource "local_file" "uniconn_key_pem" {
  for_each = var.uniconns
  content  = aws_iot_certificate.uniconn_cert[each.key].private_key
  filename = "${path.module}/unicorns/tmp/${each.key}/x509/key.pem"
}

data "http" "aws_root_ca_pem" {
  url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
}

resource "local_file" "aws_root_ca_pem" {
  for_each = var.uniconns
  content  = data.http.aws_root_ca_pem.response_body
  filename = "${path.module}/unicorns/tmp/${each.key}/x509/ca.pem"
}

resource "null_resource" "pem_to_der" {
  for_each = var.uniconns
  triggers = {
    key = each.key
  }
  provisioner "local-exec" {
    command = "openssl x509 -in ${local_file.uniconn_cert_pem[each.key].filename} -outform der -out ${path.module}/unicorns/tmp/${each.key}/x509/cert.der"
  }
  provisioner "local-exec" {
    command = "openssl rsa -in ${local_file.uniconn_key_pem[each.key].filename} -outform der -out ${path.module}/unicorns/tmp/${each.key}/x509/key.der"
  }
  provisioner "local-exec" {
    command = "openssl x509 -in ${local_file.aws_root_ca_pem[each.key].filename} -outform der -out ${path.module}/unicorns/tmp/${each.key}/x509/ca.der"
  }
  provisioner "local-exec" {
    when = destroy
    command = "rm ${path.module}/unicorns/tmp/${each.key}/x509/*.der"
  }
}
