import pytest
import json
from unittest.mock import patch, MagicMock
from src.valida import lambda_handler

@pytest.fixture
def evento_s3():
    return {'Records': [{'s3': {'bucket': {'name': 'fake-bucket'}, 'object': {'key': 'raw/teste.json'}}}]}

@patch('src.valida.registrar_processamento')
@patch('src.valida.ja_processado')
@patch('src.valida.calcular_hash')
@patch('src.valida.s3')
def test_vendas_validas(mock_s3, mock_hash, mock_ja_proc, mock_reg, evento_s3):
    mock_hash.return_value = "hash_fake_123"
    mock_ja_proc.return_value = False
    
    vendas = [{'id_venda': 1, 'produto': 'Mouse', 'quantidade': 2, 'preco_unitario': 100.0, 'data_venda': '2026-01-01', 'regiao': 'Sudeste'}]
    mock_s3.get_object.return_value = {'Body': MagicMock(read=lambda: json.dumps(vendas).encode())}
    
    resultado = lambda_handler(evento_s3, None)
    assert resultado['validos'] == 1
    assert resultado['invalidos'] == 0

@patch('src.valida.registrar_processamento')
@patch('src.valida.ja_processado')
@patch('src.valida.calcular_hash')
@patch('src.valida.s3')
def test_duplicado(mock_s3, mock_hash, mock_ja_proc, mock_reg, evento_s3):
    mock_hash.return_value = "hash_fake_123"
    mock_ja_proc.return_value = True # Simula que já foi processado!
    
    resultado = lambda_handler(evento_s3, None)
    assert resultado['body'] == 'Duplicado ignorado'