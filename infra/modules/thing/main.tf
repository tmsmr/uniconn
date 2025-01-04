data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "random_uuid" "client_id" {
}

locals {
  iot_core_root_ca = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"

  client_arn_base      = "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:client"
  topic_arn_base       = "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic"
  topicfilter_arn_base = "${local.topic_arn_base}filter"

  client_policy_statements = [
    {
      Action = [
        "iot:Connect",
      ]
      Effect   = "Allow"
      Resource = "${local.client_arn_base}/${random_uuid.client_id.result}"
    }
  ]

  unicorn_policy_statements = concat(local.client_policy_statements, [
    {
      Action = [
        "iot:Subscribe",
      ]
      Effect   = "Allow"
      Resource = "${local.topicfilter_arn_base}/${var.prefix}/unicorn/${var.name}/*"
    },
    {
      Action = [
        "iot:Subscribe",
      ]
      Effect   = "Allow"
      Resource = "${local.topicfilter_arn_base}/${var.prefix}/all/*"
    },
    {
      Action = [
        "iot:Receive",
      ]
      Effect   = "Allow"
      Resource = "${local.topic_arn_base}/${var.prefix}/unicorn/${var.name}/*"
    },
    {
      Action = [
        "iot:Receive",
      ]
      Effect   = "Allow"
      Resource = "${local.topic_arn_base}/${var.prefix}/all/*"
    },
    {
      Action = [
        "iot:Publish",
      ]
      Effect   = "Allow"
      Resource = "${local.topic_arn_base}/${var.prefix}/status/*"
    }
  ])

  controller_policy_statements = concat(local.client_policy_statements, [
    {
      Action = [
        "iot:Subscribe",
      ]
      Effect   = "Allow"
      Resource = "${local.topicfilter_arn_base}/${var.prefix}/status/*"
    },
    {
      Action = [
        "iot:Receive",
      ]
      Effect   = "Allow"
      Resource = "${local.topic_arn_base}/${var.prefix}/status/*"
    },
    {
      Action = [
        "iot:Publish",
      ]
      Effect   = "Allow"
      Resource = "${local.topic_arn_base}/${var.prefix}/*"
    }
  ])
}

data "aws_iot_endpoint" "current" {
  endpoint_type = "iot:Data-ATS"
}

resource "aws_iot_certificate" "cert" {
  active = true
}

resource "aws_iot_policy" "policy" {
  name = "${var.prefix}-${var.type}-${var.name}"
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = var.type == "unicorn" ? local.unicorn_policy_statements : local.controller_policy_statements
  })
}

resource "aws_iot_thing" "thing" {
  name = "${var.prefix}-${var.type}-${var.name}"
}

resource "aws_iot_policy_attachment" "policy_attachment" {
  policy = aws_iot_policy.policy.name
  target = aws_iot_certificate.cert.arn
}

resource "aws_iot_thing_principal_attachment" "principal_attachment" {
  principal = aws_iot_certificate.cert.arn
  thing     = aws_iot_thing.thing.name
}

resource "local_file" "cert_pem" {
  content  = aws_iot_certificate.cert.certificate_pem
  filename = "${var.x509_dir}/cert.pem"
}

resource "local_file" "key_pem" {
  content  = aws_iot_certificate.cert.private_key
  filename = "${var.x509_dir}/key.pem"
}

data "http" "ca_pem" {
  url = local.iot_core_root_ca
}

resource "local_file" "ca_pem" {
  content  = data.http.ca_pem.response_body
  filename = "${var.x509_dir}/ca.pem"
}

resource "null_resource" "pem_to_der" {
  provisioner "local-exec" {
    command = "openssl x509 -in ${local_file.cert_pem.filename} -outform der -out ${var.x509_dir}/cert.der"
  }
  provisioner "local-exec" {
    command = "openssl rsa -in ${local_file.key_pem.filename} -outform der -out ${var.x509_dir}/key.der"
  }
  provisioner "local-exec" {
    command = "openssl x509 -in ${local_file.ca_pem.filename} -outform der -out ${var.x509_dir}/ca.der"
  }
}
