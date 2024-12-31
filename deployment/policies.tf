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
        Sid = "AllowConnect"
        Action = [
          "iot:Connect",
        ]
        Effect   = "Allow"
        Resource = "${local.client_arn_base}/${random_uuid.uniconn_client_id[each.key].result}"
      },
      {
        Sid = "AllowSubscribe"
        Action = [
          "iot:Subscribe",
        ]
        Effect   = "Allow"
        Resource = "${local.topicfilter_arn_base}/${random_pet.deployment_id.id}/${each.key}/pixels"
      },
      {
        Sid = "AllowSubscribeBroadcast"
        Action = [
          "iot:Subscribe",
        ]
        Effect   = "Allow"
        Resource = "${local.topicfilter_arn_base}/${random_pet.deployment_id.id}/pixels"
      },
      {
        Sid = "AllowReceive"
        Action = [
          "iot:Receive",
        ]
        Effect   = "Allow"
        Resource = "${local.topic_arn_base}/${random_pet.deployment_id.id}/${each.key}/pixels"
      },
      {
        Sid = "AllowReceiveBroadcast"
        Action = [
          "iot:Receive",
        ]
        Effect   = "Allow"
        Resource = "${local.topic_arn_base}/${random_pet.deployment_id.id}/pixels"
      }
    ]
  })
}
