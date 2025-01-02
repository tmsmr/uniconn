output "mqtt_conn_config" {
  value = {
    mqtt_host      = data.aws_iot_endpoint.current.endpoint_address
    mqtt_port      = 8883
    mqtt_client_id = random_uuid.client_id.result
  }
}
