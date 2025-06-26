"""
This file defines the database models
"""

from pydal.validators import *
from datetime import datetime
from . import settings

from .common import Field, db

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

# Tabela de funcionários
db.define_table(
    'funcionario',
    # Dados pessoais
    Field('nome', 'string', required=True, 
          requires=IS_LENGTH(maxsize=100, error_message='Nome deve ter no máximo 100 caracteres')),
    Field('cpf', 'string', required=True, unique=True,
          requires=IS_MATCH('^\d{3}\.\d{3}\.\d{3}-\d{2}$', error_message='CPF deve estar no formato 000.000.000-00')),
    Field('rg', 'string', required=True,
          requires=IS_LENGTH(maxsize=20, error_message='RG deve ter no máximo 20 caracteres')),
    Field('idade', 'integer',
          requires=IS_INT_IN_RANGE(16, 100, error_message='Idade deve estar entre 16 e 100 anos')),
    Field('estado_civil', 'string', 
          requires=IS_IN_SET(['Solteiro', 'Casado', 'Divorciado', 'Viúvo', 'União Estável'], 
                            error_message='Estado civil inválido')),
    Field('sexo', 'string', 
          requires=IS_IN_SET(['Masculino', 'Feminino', 'Outro'], 
                            error_message='Sexo inválido')),
    Field('data_nascimento', 'date',
          requires=IS_DATE(format='%Y-%m-%d', error_message='Data de nascimento inválida')),

    # Endereço
    Field('rua', 'string',
          requires=IS_LENGTH(maxsize=200, error_message='Rua deve ter no máximo 200 caracteres')),
    Field('bairro', 'string',
          requires=IS_LENGTH(maxsize=100, error_message='Bairro deve ter no máximo 100 caracteres')),
    Field('cidade', 'string', required=True,
          requires=IS_LENGTH(maxsize=100, error_message='Cidade deve ter no máximo 100 caracteres')),
    Field('cep', 'string',
          requires=IS_MATCH('^\d{5}-\d{3}$', error_message='CEP deve estar no formato 00000-000')),
    Field('estado', 'string', required=True,
          requires=IS_IN_SET(['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 
                              'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 
                              'SP', 'SE', 'TO'], 
                            error_message='Estado inválido')),

    # Cargo
    Field('data_entrada', 'date',
          requires=IS_DATE(format='%Y-%m-%d', error_message='Data de entrada inválida')),
    Field('cargo', 'string',
          requires=IS_LENGTH(maxsize=100, error_message='Cargo deve ter no máximo 100 caracteres')),
    Field('salario', 'decimal(10,2)',
          requires=IS_DECIMAL_IN_RANGE(0, 999999.99, error_message='Salário deve ser um valor válido')),

    # Campos de auditoria
    Field('created_on', 'datetime', default=datetime.now, writable=False),
    Field('updated_on', 'datetime', default=datetime.now, update=datetime.now, writable=False),

    format='%(nome)s'
)

# Tabela de contratos gerados para funcionários
db.define_table(
    'contrato',
    Field('funcionario', 'reference funcionario', required=True,
          requires=IS_IN_DB(db, 'funcionario.id', '%(nome)s', error_message='Funcionário inválido')),
    Field('arquivo', 'upload', required=True, 
          requires=IS_NOT_EMPTY(error_message='Arquivo é obrigatório')),
    Field('status', 'string', required=True, default='aguardando assinatura', 
          requires=IS_IN_SET(['aguardando assinatura', 'assinado'], 
                            error_message='Status inválido')),
    Field('data_geracao', 'datetime', default=datetime.now, writable=False),
    Field('arquivo_assinado', 'upload'),  # Arquivo do contrato assinado
    Field('data_assinatura', 'datetime'),  # Data da assinatura
    
    # Campos de auditoria
    Field('created_on', 'datetime', default=datetime.now, writable=False),
    Field('updated_on', 'datetime', default=datetime.now, update=datetime.now, writable=False),
    
    format='%(arquivo)s'
)

# Configurar relacionamentos
db.contrato.funcionario.requires = IS_IN_DB(db, 'funcionario.id', '%(nome)s')

db.contrato.arquivo.upload_path = settings.UPLOAD_FOLDER
db.contrato.arquivo_assinado.upload_path = settings.UPLOAD_FOLDER
db.contrato.arquivo.download_url = lambda filename: URL('uploads/%s' % filename)
db.contrato.arquivo_assinado.download_url = lambda filename: URL('uploads/%s' % filename)

# Índices para melhor performance
db.executesql('CREATE INDEX IF NOT EXISTS idx_funcionario_cpf ON funcionario(cpf);')
db.executesql('CREATE INDEX IF NOT EXISTS idx_contrato_funcionario ON contrato(funcionario);')
db.executesql('CREATE INDEX IF NOT EXISTS idx_contrato_status ON contrato(status);')
db.executesql('CREATE INDEX IF NOT EXISTS idx_contrato_data_geracao ON contrato(data_geracao);')

db.commit()
