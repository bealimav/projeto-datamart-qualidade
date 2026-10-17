# 🛡️ DataMart Analytics - Projeto 3: Qualidade e Idempotência

Este projeto evolui o pipeline dos projetos anteriores adicionando duas camadas críticas de confiabilidade: **Idempotência** (garantia de que dados não serão duplicados) e **Qualidade de Dados** (separação automática de registros corrompidos).

![AWS](https://img.shields.io/badge/AWS-Serverless-orange)
![Terraform](https://img.shields.io/badge/Terraform-1.5+-purple)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Pytest](https://img.shields.io/badge/Testes-Pytest-green)
![CI/CD](https://img.shields.io/badge/CI--CD-GitHub_Actions-black)
![Tests](https://github.com/bealimav/projeto-datamart-qualidade/actions/workflows/tests.yml/badge.svg)

---

## 🎯 O Problema de Negócio

Em pipelines reais, falhas de rede ou retries do S3 podem acionar a mesma função Lambda duas vezes, gerando duplicação de vendas e relatórios contábeis errados. Além disso, dados enviados pelas fontes podem vir com erros (quantidades negativas, campos nulos), sujando o Data Lake.

---

## 🛠️ A Solução Implementada

1. **Idempotência com DynamoDB:** A cada arquivo recebido, a Lambda calcula um hash SHA-256. Se o hash já existir na tabela DynamoDB, o processamento é abortado.
2. **Quarentena Inteligente:** Dados inválidos vão para uma camada de `quarentena/` com metadados explicando o motivo da rejeição.
3. **Testes Automatizados:** A lógica da Lambda é coberta por testes unitários (`pytest` + `mock`).
4. **Infrastructure as Code:** Toda a stack provisionada via Terraform.

---

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

---

## 🚀 CI/CD (Integração Contínua)

Este projeto conta com uma esteira automatizada de **GitHub Actions** (`.github/workflows/tests.yml`). A cada `git push`:
1. Uma máquina virtual Ubuntu é iniciada.
2. O Python 3.12 e as dependências são instalados.
3. Variáveis de ambiente simuladas garantem a inicialização do `boto3`.
4. Os testes unitários (`pytest`) são executados.

Isso garante que qualquer alteração no código da Lambda que quebre a regra de idempotência seja barrada antes de ir para produção.

---

## 📁 Estrutura do Projeto

```text
projeto-datamart-qualidade/
├── .github/workflows/
│   └── tests.yml            # CI/CD de testes automatizados
├── src/
│   └── valida.py            # Código da Lambda
├── scripts/
│   ├── gerador.py           # Gera dados sintéticos
│   └── etl_local.py         # Transforma trusted → refined
├── tests/
│   └── test_valida.py       # Testes unitários com Pytest
├── terraform/
│   ├── main.tf, s3.tf, dynamodb.tf, iam.tf, lambda.tf
└── README.md
```

---

## 🚀 Como Reproduzir

### 1. Rodar os Testes Unitários (Sem gastar AWS)
```bash
py -m pip install -r requirements.txt
py -m pytest tests/ -v
```

### 2. Provisionar a Infraestrutura
```bash
cd terraform
terraform init
terraform apply -auto-approve
cd ..
```

### 3. Testar o Pipeline Completo
```bash
py scripts/gerador.py
py scripts/etl_local.py
```

### 4. Destruir tudo (FinOps)
```bash
cd terraform
terraform destroy -auto-approve
```

---

## ⚠️ Nota Técnica de Troubleshooting

**Problema conhecido:** Foi identificada uma instabilidade no provisionamento do gatilho (Trigger) nativo do S3 via Terraform em contas novas. Em um ambiente de produção, a solução de contorno recomendada seria utilizar o **Amazon EventBridge** para rotear os eventos do S3 para a Lambda, garantindo maior resiliência.

---

## 📚 Aprendizados

- Implementação de idempotência usando hash SHA-256 e DynamoDB.
- Criação de camada de quarentena com metadados de auditoria.
- Escrita de testes unitários com Pytest e mock de serviços AWS.
- Implementação de **CI/CD** para testes automatizados (GitHub Actions).
- TTL (Time To Live) no DynamoDB para controle de custos.

---

## 👩‍💻 Autora
Beatriz Lima — Estagiária de Engenharia de Dados
