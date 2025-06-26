"""
This file defines the database models
"""

from pydal.validators import *
from datetime import datetime
from . import settings
from .constants import (
    BRAZILIAN_STATES, MARITAL_STATUS, GENDER_OPTIONS, VALIDATION_PATTERNS,
    VALIDATION_RANGES, FIELD_LENGTHS, DATABASE_INDEXES, CONTRACT_STATUS
)

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
          requires=IS_LENGTH(maxsize=FIELD_LENGTHS['NOME_MAX'], 
                           error_message=f'Nome deve ter no máximo {FIELD_LENGTHS["NOME_MAX"]} caracteres')),
    Field('cpf', 'string', required=True, unique=True,
          requires=IS_MATCH(VALIDATION_PATTERNS['CPF'], 
                           error_message='CPF deve estar no formato 000.000.000-00')),
    Field('rg', 'string', required=True,
          requires=IS_LENGTH(maxsize=FIELD_LENGTHS['RG_MAX'], 
                           error_message=f'RG deve ter no máximo {FIELD_LENGTHS["RG_MAX"]} caracteres')),
    Field('idade', 'integer',
          requires=IS_INT_IN_RANGE(VALIDATION_RANGES['AGE_MIN'], VALIDATION_RANGES['AGE_MAX'], 
                                  error_message=f'Idade deve estar entre {VALIDATION_RANGES["AGE_MIN"]} e {VALIDATION_RANGES["AGE_MAX"]} anos')),
    Field('estado_civil', 'string', 
          requires=IS_IN_SET(MARITAL_STATUS, error_message='Estado civil inválido')),
    Field('sexo', 'string', 
          requires=IS_IN_SET(GENDER_OPTIONS, error_message='Sexo inválido')),
    Field('data_nascimento', 'date',
          requires=IS_DATE(format='%Y-%m-%d', error_message='Data de nascimento inválida')),

    # Endereço
    Field('rua', 'string',
          requires=IS_LENGTH(maxsize=FIELD_LENGTHS['RUA_MAX'], 
                           error_message=f'Rua deve ter no máximo {FIELD_LENGTHS["RUA_MAX"]} caracteres')),
    Field('bairro', 'string',
          requires=IS_LENGTH(maxsize=FIELD_LENGTHS['BAIRRO_MAX'], 
                           error_message=f'Bairro deve ter no máximo {FIELD_LENGTHS["BAIRRO_MAX"]} caracteres')),
    Field('cidade', 'string', required=True,
          requires=IS_LENGTH(maxsize=FIELD_LENGTHS['CIDADE_MAX'], 
                           error_message=f'Cidade deve ter no máximo {FIELD_LENGTHS["CIDADE_MAX"]} caracteres')),
    Field('cep', 'string',
          requires=IS_MATCH(VALIDATION_PATTERNS['CEP'], 
                           error_message='CEP deve estar no formato 00000-000')),
    Field('estado', 'string', required=True,
          requires=IS_IN_SET(BRAZILIAN_STATES, error_message='Estado inválido')),

    # Cargo
    Field('data_entrada', 'date',
          requires=IS_DATE(format='%Y-%m-%d', error_message='Data de entrada inválida')),
    Field('cargo', 'string',
          requires=IS_LENGTH(maxsize=FIELD_LENGTHS['CARGO_MAX'], 
                           error_message=f'Cargo deve ter no máximo {FIELD_LENGTHS["CARGO_MAX"]} caracteres')),
    Field('salario', 'decimal(10,2)',
          requires=IS_DECIMAL_IN_RANGE(VALIDATION_RANGES['SALARY_MIN'], VALIDATION_RANGES['SALARY_MAX'], 
                                      error_message='Salário deve ser um valor válido')),

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
    Field('status', 'string', required=True, default=CONTRACT_STATUS['AGUARDANDO_ASSINATURA'], 
          requires=IS_IN_SET(list(CONTRACT_STATUS.values()), error_message='Status inválido')),
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

# Criar índices para melhor performance
for index_sql in DATABASE_INDEXES:
    db.executesql(index_sql)

db.commit()
