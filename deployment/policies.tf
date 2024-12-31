locals {
  client_arn_base      = "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:client"
  topic_arn_base       = "arn:aws:iot:${var.aws_region}:${data.aws_caller_identity.current.account_id}:topic"
  topicfilter_arn_base = "${local.topic_arn_base}filter"
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
        ]
        Effect   = "Allow"
        Resource = "${local.topicfilter_arn_base}/${random_pet.deployment_id.id}/${each.key}/*"
      },
      {
        Action = [
          "iot:Subscribe",
        ]
        Effect   = "Allow"
        Resource = "${local.topicfilter_arn_base}/${random_pet.deployment_id.id}/all/*"
      },
      {
        Action = [
          "iot:Receive",
        ]
        Effect   = "Allow"
        Resource = "${local.topic_arn_base}/${random_pet.deployment_id.id}/${each.key}/*"
      },
      {
        Action = [
          "iot:Receive",
        ]
        Effect   = "Allow"
        Resource = "${local.topic_arn_base}/${random_pet.deployment_id.id}/all/*"
      }
    ]
  })
}

resource "aws_iot_policy" "client_policy" {
  for_each = var.clients
  name     = "client-policy-${each.key}-${random_pet.deployment_id.id}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "iot:Connect",
        ]
        Effect   = "Allow"
        Resource = "${local.client_arn_base}/${random_uuid.client_client_id[each.key].result}"
      },
      {
        Action = [
          "iot:Publish",
        ]
        Effect   = "Allow"
        Resource = "${local.topic_arn_base}/${random_pet.deployment_id.id}/*"
      }
    ]
  })
}
