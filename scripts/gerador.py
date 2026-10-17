import boto3
import json
import random
from datetime import datetime, timedelta
from faker import Faker
import os

fake = Faker('pt_BR')
s3 = boto3.client('s3')

def descobrir_bucket():
    # Busca o bucket do projeto 3
    buckets = s3.list_buckets()['Buckets']
    for b in buckets:
        if 'datamart-qualidade-datalake' in b['Name']:
            return b['Name']
    raise Exception("Bucket não encontrado")

def gerar_venda():
    return {
        "id_venda": random.randint(1000, 9999),
        "produto": random.choice(['Notebook', 'Mouse', 'Teclado', 'Monitor', 'Headset']),
        "quantidade": random.randint(1, 5),
        "preco_unitario": round(random.uniform(50.0, 5000.0), 2),
        "data_venda": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
        "regiao": random.choice(['Sudeste', 'Sul', 'Nordeste']),
        "canal_venda": random.choice(['site', 'app'])
    }

def upload_vendas(quantidade=50):
    bucket = descobrir_bucket()
    vendas = [gerar_venda() for _ in range(quantidade)]
    
    # Vamos forçar alguns erros para testar a quarentena!
    if quantidade > 10:
        vendas[0]['quantidade'] = -5  # Erro de negócio
        del vendas[1]['produto']      # Erro de schema
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    key = f"raw/vendas_{timestamp}.json"
    
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(vendas, ensure_ascii=False), ContentType='application/json')
    print(f"✅ {quantidade} vendas enviadas para s3://{bucket}/{key}")
    print(f"👉 Dica: Copie o nome do arquivo acima para testar a idempotência depois!")

if __name__ == "__main__":
    upload_vendas(20)