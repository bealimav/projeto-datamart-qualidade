import json
import urllib.parse
import boto3
import hashlib
import os
from datetime import datetime, timedelta

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Pega o nome da tabela via variável de ambiente (boa prática)
TABELA_NOME = os.environ.get('DYNAMODB_TABLE', 'datamart-qualidade-controle-dev')
tabela = dynamodb.Table(TABELA_NOME)

CAMPOS_OBRIGATORIOS = ['id_venda', 'produto', 'quantidade', 'preco_unitario', 'data_venda', 'regiao']

def calcular_hash(bucket, key):
    """Calcula hash SHA-256 do conteúdo do arquivo."""
    response = s3.get_object(Bucket=bucket, Key=key)
    conteudo = response['Body'].read()
    return hashlib.sha256(conteudo).hexdigest()

def ja_processado(hash_arquivo):
    """Verifica se o hash já existe no DynamoDB."""
    response = tabela.get_item(Key={'hash_arquivo': hash_arquivo})
    return 'Item' in response

def registrar_processamento(hash_arquivo, key):
    """Salva o hash no DynamoDB com TTL de 30 dias."""
    tabela.put_item(Item={
        'hash_arquivo': hash_arquivo,
        's3_key': key,
        'timestamp': datetime.utcnow().isoformat(),
        'expira_em': int((datetime.utcnow() + timedelta(days=30)).timestamp())
    })

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    print(f"📥 Processando: s3://{bucket}/{key}")
    
    try:
        # 1. Verifica Idempotência (se já foi processado)
        hash_arquivo = calcular_hash(bucket, key)
        if ja_processado(hash_arquivo):
            print("⏭️ Arquivo duplicado. Ignorando.")
            return {'statusCode': 200, 'body': 'Duplicado ignorado'}
        
        # 2. Lê o arquivo
        response = s3.get_object(Bucket=bucket, Key=key)
        conteudo = json.loads(response['Body'].read().decode('utf-8'))
        
        validos = []
        invalidos = []
        
        # 3. Validação de Qualidade
        for venda in conteudo:
            erros = [c for c in CAMPOS_OBRIGATORIOS if c not in venda]
            
            if venda.get('quantidade', 0) <= 0:
                erros.append('quantidade_invalida')
            if venda.get('preco_unitario', 0) <= 0:
                erros.append('preco_invalido')
            
            if erros:
                venda['_motivo_rejeicao'] = erros
                venda['_timestamp_rejeicao'] = datetime.utcnow().isoformat()
                invalidos.append(venda)
            else:
                venda['_ingestao_ts'] = datetime.utcnow().isoformat()
                validos.append(venda)
        
        # 4. Salva válidos (trusted)
        if validos:
            nova_key = key.replace('raw/', 'trusted/')
            s3.put_object(Bucket=bucket, Key=nova_key, Body=json.dumps(validos, ensure_ascii=False))
            print(f"✅ {len(validos)} válidos salvos em {nova_key}")
        
        # 5. Salva inválidos (quarentena)
        if invalidos:
            quarentena_key = key.replace('raw/', 'quarentena/')
            s3.put_object(Bucket=bucket, Key=quarentena_key, Body=json.dumps(invalidos, ensure_ascii=False))
            print(f"⚠️ {len(invalidos)} inválidos em quarentena.")
        
        # 6. Registra sucesso
        registrar_processamento(hash_arquivo, key)
        return {'statusCode': 200, 'validos': len(validos), 'invalidos': len(invalidos)}
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise e