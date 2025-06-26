"""
Constants for the RH Contract application
"""

# Contract types
CONTRACT_TYPES = {
    'CONTRATO_ENTRADA': 'contrato_entrada',
    'TERMO_USO': 'termo_uso',
    'SINDICATO': 'sindicato'
}

# Contract statuses
CONTRACT_STATUS = {
    'AGUARDANDO_ASSINATURA': 'aguardando assinatura',
    'ASSINADO': 'assinado'
}

# Employee states
BRAZILIAN_STATES = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 
    'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 
    'SP', 'SE', 'TO'
]

# Employee marital status
MARITAL_STATUS = [
    'Solteiro', 'Casado', 'Divorciado', 'Viúvo', 'União Estável'
]

# Employee gender
GENDER_OPTIONS = [
    'Masculino', 'Feminino', 'Outro'
]

# Default values
DEFAULT_VALUES = {
    'CARGA_HORARIA': '40',
    'DIAS_SEMANA': 'Segunda a Sexta',
    'CTPS': 'Nº da CTPS'
}

# File extensions
ALLOWED_FILE_EXTENSIONS = ['.pdf']

# HTTP status codes
HTTP_STATUS = {
    'OK': 200,
    'CREATED': 201,
    'BAD_REQUEST': 400,
    'NOT_FOUND': 404,
    'INTERNAL_SERVER_ERROR': 500
}

# Response messages
MESSAGES = {
    'EMPLOYEE_NOT_FOUND': 'Funcionário não encontrado',
    'CONTRACT_NOT_FOUND': 'Contrato não encontrado',
    'TEMPLATE_NOT_FOUND': 'Template de contrato não encontrado',
    'INVALID_EMPLOYEE_ID': 'ID do funcionário inválido',
    'INVALID_FILE': 'Arquivo inválido',
    'FILE_TOO_LARGE': 'Arquivo muito grande',
    'NO_FILE_SENT': 'Nenhum arquivo foi enviado',
    'CONTRACT_SIGNED_SUCCESS': 'Contrato assinado com sucesso!',
    'REQUIRED_FIELDS': 'ID do funcionário e tipo de contrato são obrigatórios',
    'PROCESSING_ERROR': 'Erro ao processar a requisição',
    'FILE_PROCESSING_ERROR': 'Erro ao processar arquivo'
}

# Validation patterns
VALIDATION_PATTERNS = {
    'CPF': r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
    'CEP': r'^\d{5}-\d{3}$'
}

# Validation ranges
VALIDATION_RANGES = {
    'AGE_MIN': 16,
    'AGE_MAX': 100,
    'SALARY_MIN': 0,
    'SALARY_MAX': 999999.99
}

# Field lengths
FIELD_LENGTHS = {
    'NOME_MAX': 100,
    'RG_MAX': 20,
    'RUA_MAX': 200,
    'BAIRRO_MAX': 100,
    'CIDADE_MAX': 100,
    'CARGO_MAX': 100
}

# Date formats
DATE_FORMATS = {
    'DISPLAY': '%d/%m/%Y',
    'DATABASE': '%Y-%m-%d',
    'FILENAME': '%Y%m%d%H%M%S'
}

# CSS classes
CSS_CLASSES = {
    'CONTRACT_CONTAINER': 'contrato',
    'PERSONAL_DATA': 'dados-pessoais',
    'SIGNATURES': 'assinaturas',
    'SIGNATURE': 'assinatura'
}

# Database indexes
DATABASE_INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_funcionario_cpf ON funcionario(cpf);',
    'CREATE INDEX IF NOT EXISTS idx_contrato_funcionario ON contrato(funcionario);',
    'CREATE INDEX IF NOT EXISTS idx_contrato_status ON contrato(status);',
    'CREATE INDEX IF NOT EXISTS idx_contrato_data_geracao ON contrato(data_geracao);'
] 