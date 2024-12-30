locals {
  client_arn_base = "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:client"
  topic_arn_base  = "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:topic"
}

resource "aws_iot_policy" "uniconn_policy" {
  for_each = var.uniconns
  name     = "uniconn-policy-${each.key}-${random_pet.deployment_id.id}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "iot:Connect",
        ]
        Effect   = "Allow"
        Resource = "${local.client_arn_base}/${random_uuid.uniconn_client_id[each.key].result}"
      },
      {
        Action = [
          "iot:Subscribe",
          "iot:Receive",
        ]
        Effect   = "Allow"
        Resource = "${local.topic_arn_base}/${each.key}-${random_pet.deployment_id.id}"
      },
      {
        Action = [
          "iot:Subscribe",
          "iot:Receive",
        ]
        Effect   = "Allow"
        Resource = "${local.topic_arn_base}/${random_pet.deployment_id.id}"
      },
    ]
  })
}
