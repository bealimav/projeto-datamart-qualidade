import boto3
import pandas as pd
import json
import io
from datetime import datetime

s3 = boto3.client('s3')

def descobrir_bucket():
    buckets = s3.list_buckets()['Buckets']
    for b in buckets:
        if 'datamart-qualidade-datalake' in b['Name']:
            return b['Name']
    raise Exception("Bucket não encontrado")

def processar():
    bucket = descobrir_bucket()
    response = s3.list_objects_v2(Bucket=bucket, Prefix='trusted/')
    if 'Contents' not in response:
        print("Nenhum arquivo em trusted.")
        return

    dfs = []
    for obj in response['Contents']:
        if obj['Key'].endswith('.json'):
            data = s3.get_object(Bucket=bucket, Key=obj['Key'])
            dfs.append(pd.DataFrame(json.loads(data['Body'].read().decode('utf-8'))))
    
    if not dfs:
        return
        
    df = pd.concat(dfs, ignore_index=True)
    df['valor_total'] = df['quantidade'] * df['preco_unitario']
    df = df.drop_duplicates(subset=['id_venda'])
    df['data_venda'] = pd.to_datetime(df['data_venda'])
    
    # Salva Parquet
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    key = f"refined/vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
    s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
    print(f"✅ Parquet salvo em s3://{bucket}/{key} com {len(df)} vendas válidas.")

if __name__ == "__main__":
    processar()