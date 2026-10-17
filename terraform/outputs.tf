output "bucket_name" {
  value = aws_s3_bucket.datalake.id
}

output "dynamodb_table" {
  value = aws_dynamodb_table.controle_processamento.name
}

output "lambda_function_name" {
  value = aws_lambda_function.valida_ingestao.function_name
}