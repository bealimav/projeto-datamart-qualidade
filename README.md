# 🛡️ DataMart Analytics - Projeto 3: Qualidade e Idempotência

Este projeto evolui o pipeline dos projetos anteriores adicionando duas camadas críticas de confiabilidade para Engenharia de Dados em produção: **Idempotência** (garantia de que dados não serão duplicados) e **Qualidade de Dados** (separação automática de registros corrompidos).

![AWS](https://img.shields.io/badge/AWS-Serverless-orange)
![Terraform](https://img.shields.io/badge/Terraform-1.5+-purple)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Pytest](https://img.shields.io/badge/Testes-Pytest-green)
![Status](https://img.shields.io/badge/Status-Completo-green)

## 🎯 O Problema de Negócio

Em pipelines reais, falhas de rede ou retries do S3 podem acionar a mesma função Lambda duas vezes, gerando duplicação de vendas e relatórios contábeis errados. Além disso, dados enviados pelas fontes podem vir com erros (quantidades negativas, campos nulos), sujando o Data Lake e quebrando o processo de análise.

## 🛠️ A Solução Implementada

1. **Idempotência com DynamoDB:** A cada arquivo recebido, a Lambda calcula um hash SHA-256 do conteúdo. Se o hash já existir na tabela DynamoDB, o processamento é abortado, garantindo que o mesmo dado nunca seja contado duas vezes.
2. **Quarentena Inteligente:** Os dados passam por validações de schema e regras de negócio. Vendas inválidas não são descartadas silenciosamente; elas vão para uma camada de `quarentena/` com metadados (`_motivo_rejeicao`, `_timestamp_rejeicao`) para posterior análise.
3. **Testes Automatizados:** A lógica da Lambda é coberta por testes unitários (`pytest` + `unittest.mock`), garantindo que a função funcione sem precisar fazer deploy na AWS.
4. **Infrastructure as Code:** Toda a stack (S3, Lambda, IAM, DynamoDB) é provisionada via Terraform.

## 🏗️ Arquitetura

```text
[Gerador] → [S3 raw/] → [Lambda] → (DynamoDB: checa Hash SHA-256)
                            ↓
                  [S3 trusted/] (dados válidos)
                            ↓
                  [S3 quarentena/] (dados ruins + logs de erro)
                            ↓
                  [ETL Local] → [S3 refined/] (Parquet)
```

## 🛠️ Tecnologias Utilizadas

- **Amazon S3** — Data Lake em camadas (raw, trusted, quarentena, refined).
- **AWS Lambda** (Python 3.12) — Processamento orientado a eventos.
- **Amazon DynamoDB** — Controle de idempotência e TTL para limpeza.
- **Terraform** — Provisionamento de infraestrutura.
- **Python + Pandas + PyArrow** — ETL e transformação.
- **Pytest + Mock** — Testes unitários.

## 📁 Estrutura do Projeto

```text
projeto-datamart-qualidade/
├── src/
│   └── valida.py            # Código da Lambda (Hash, Idempotência, Quarentena)
├── scripts/
│   ├── gerador.py           # Gera dados sintéticos (incluindo propositalmente inválidos)
│   └── etl_local.py         # Transforma trusted/ em refined/ (Parquet)
├── tests/
│   └── test_valida.py       # Testes unitários com mock da AWS
├── terraform/
│   ├── main.tf, s3.tf, dynamodb.tf, iam.tf, lambda.tf, variables.tf, outputs.tf
└── README.md
```

## 🚀 Como Reproduzir

### Pré-requisitos
- Terraform >= 1.5.0
- AWS CLI configurado
- Python 3.10+ com as dependências: `py -m pip install -r requirements.txt`

### 1. Rodar os Testes Unitários (Sem gastar AWS)
```bash
py -m pytest tests/ -v
```
Você deve ver os testes passando, comprovando a lógica de idempotência e validação.

### 2. Provisionar a Infraestrutura
```bash
cd terraform
terraform init
terraform apply -auto-approve
cd ..
```

### 3. Testar o Pipeline Completo
```bash
# Gera os dados (envia para raw/)
py scripts/gerador.py

# Roda o ETL para gerar Parquet (lê de trusted/)
py scripts/etl_local.py
```

### 4. Destruir tudo (FinOps)
```bash
cd terraform
terraform destroy -auto-approve
```

## ⚠️ Nota Técnica de Troubleshooting

Durante o desenvolvimento, o pipeline foi validado com sucesso através de:
1. Testes unitários locais (`pytest`).
2. Invocação manual da função Lambda com payloads simulados do S3, comprovando a lógica de idempotência (DynamoDB) e validação.

**Problema conhecido:** Foi identificada uma instabilidade no provisionamento do gatilho (Trigger) nativo do S3 via Terraform, onde o evento `ObjectCreated` não dispara a função, mesmo com as permissões IAM e notificações configuradas corretamente. Em um ambiente de produção, a solução de contorno recomendada seria utilizar o **Amazon EventBridge** para rotear os eventos do S3 para a Lambda, garantindo maior resiliência.

## 📚 Aprendizados

- Implementação de idempotência usando hash SHA-256 e DynamoDB.
- Criação de camada de quarentena com metadados de auditoria.
- Escrita de testes unitários com Pytest e mock de serviços AWS.
- TTL (Time To Live) no DynamoDB para controle de custos.

## 👩‍💻 Autora
Beatriz Lima — Estudante de Engenharia de Dados
