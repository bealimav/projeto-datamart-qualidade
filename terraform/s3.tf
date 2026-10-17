resource "aws_s3_bucket" "datalake" {
  bucket        = "${var.projeto}-datalake-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "datalake" {
  bucket                  = aws_s3_bucket.datalake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "pastas" {
  for_each = toset(["raw/", "trusted/", "refined/", "quarentena/", "athena-results/"])
  bucket   = aws_s3_bucket.datalake.id
  key      = each.value
}