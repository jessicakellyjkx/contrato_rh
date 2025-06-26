"""
Configurações do aplicativo de Contratos RH
"""

import os

# Configurações do PDF
PDF_CONFIG = {
    'wkhtmltopdf_path': '/usr/bin/wkhtmltopdf',
    'page_size': 'A4',
    'orientation': 'portrait',
    'margin_top': '1cm',
    'margin_right': '1cm',
    'margin_bottom': '1cm',
    'margin_left': '1cm'
}

# Configurações da empresa
EMPRESA_CONFIG = {
    'nome': 'Nome da Empresa',
    'cnpj': '00.000.000/0000-00',
    'endereco': 'Endereço da Empresa',
    'cidade': 'Cidade da Empresa',
    'estado': 'Estado da Empresa',
    'cep': '00000-000'
}

# Configurações de upload
UPLOAD_CONFIG = {
    'allowed_extensions': ['.pdf'],
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'upload_folder': 'uploads'
}

# Configurações de paginação
PAGINATION_CONFIG = {
    'items_per_page': 20,
    'max_items_per_page': 100
}

# Configurações de busca
SEARCH_CONFIG = {
    'max_results': 10,
    'min_query_length': 2
}

# Configurações de cache
CACHE_CONFIG = {
    'enabled': True,
    'timeout': 300  # 5 minutos
}

# Configurações de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'app.log'
} 