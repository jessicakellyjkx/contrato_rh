"""
This file defines the database models
"""

from pydal.validators import *

from .common import Field, db

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

db.define_table(
    'funcionario',
    # Dados pessoais
    Field('nome', 'string', required=True),
    Field('cpf', 'string', required=True, unique=True),
    Field('rg', 'string', required=True),
    Field('idade', 'integer'),
    Field('estado_civil', 'string', requires=IS_IN_SET(['Solteiro', 'Casado', 'Divorciado', 'Viúvo', 'União Estável'])),
    Field('sexo', 'string', requires=IS_IN_SET(['Masculino', 'Feminino', 'Outro'])),
    Field('data_nascicmento', 'date'),

    # Endereço
    Field('rua', 'string'),
    Field('bairro', 'string'),
    Field('cidade', 'string'),
    Field('cep', 'string'),
    Field('estado', 'string'),

    # Cargo
    Field('data_entrada', 'date'),
    Field('cargo', 'string'),
    Field('salario', 'decimal(10,2)'),

    format='%(nome)s'
)
