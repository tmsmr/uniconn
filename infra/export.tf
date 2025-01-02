resource "local_file" "unicorn_config" {
  for_each = module.unicorn
  content = jsonencode(merge(each.value.mqtt_conn_config, {
    mqtt_topic_base     = "${random_pet.deployment.id}/${each.key}"
    mqtt_all_topic_base = "${random_pet.deployment.id}/all"
    unicorn_type        = var.unicorns[each.key].unicorn_type
    wifi_ssid           = var.unicorns[each.key].wifi_ssid
    wifi_psk            = var.unicorns[each.key].wifi_psk
    wifi_country        = var.unicorns[each.key].wifi_country
  }))
  filename = "${path.root}/configs/tmp/${each.key}/config.json"
}

resource "local_file" "controller_config" {
  for_each = module.controller
  content = jsonencode(merge(each.value.mqtt_conn_config, {
    unicorns = [
      for name, unicorn in module.unicorn : {
        unicorn_name = name
        unicorn_type = var.unicorns[name].unicorn_type
        topic_base   = "${random_pet.deployment.id}/${name}"
      }
    ]
  }))
  filename = "${path.root}/configs/tmp/${each.key}/config.json"
}

resource "archive_file" "unicorn_export" {
  for_each   = module.unicorn
  type       = "zip"
  source_dir = "${path.root}/configs/tmp/${each.key}"
  excludes = [
    "*.pem"
  ]
  output_path = "${path.root}/configs/${each.key}.zip"
  depends_on = [
    local_file.unicorn_config
  ]
  provisioner "local-exec" {
    when    = destroy
    command = "rm ${path.root}/configs/${each.key}.zip"
  }
}

resource "archive_file" "controller_export" {
  for_each   = module.controller
  type       = "zip"
  source_dir = "${path.root}/configs/tmp/${each.key}"
  excludes = [
    "*.der"
  ]
  output_path = "${path.root}/configs/${each.key}.zip"
  depends_on = [
    local_file.controller_config
  ]
  provisioner "local-exec" {
    when    = destroy
    command = "rm ${path.root}/configs/${each.key}.zip"
  }
}
