resource "aws_dynamodb_table" "controle_processamento" {
  name         = "${var.projeto}-controle-${var.ambiente}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "hash_arquivo"

  attribute {
    name = "hash_arquivo"
    type = "S"
  }

  ttl {
    attribute_name = "expira_em"
    enabled        = true
  }
}