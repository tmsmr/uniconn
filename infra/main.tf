resource "random_pet" "deployment" {
  length = 2
}

module "unicorn" {
  for_each = var.unicorns
  source   = "./modules/thing"
  name     = each.key
  prefix   = random_pet.deployment.id
  type     = "unicorn"
  x509_dir = "${path.root}/configs/tmp/${each.key}/x509"
}

module "controller" {
  for_each = var.controllers
  source   = "./modules/thing"
  name     = each.key
  prefix   = random_pet.deployment.id
  type     = "controller"
  x509_dir = "${path.root}/configs/tmp/${each.key}/x509"
}
