"""
Exemplos de uso das funcionalidades do sistema de contratos RH
"""

from datetime import datetime
from .utils import (
    sanitize_filename, format_currency, format_date, build_address,
    get_contract_type_from_filename, validate_file_extension,
    create_unique_filename, ensure_directory_exists
)
from .constants import (
    CONTRACT_TYPES, CONTRACT_STATUS, DEFAULT_VALUES, MESSAGES,
    DATE_FORMATS, ALLOWED_FILE_EXTENSIONS, BRAZILIAN_STATES
)


def exemplo_formatacao_dados():
    """Exemplo de uso das funções de formatação"""
    
    # Formatação de moeda
    salario = 2500.50
    salario_formatado = format_currency(salario)
    print(f"Salário formatado: {salario_formatado}")  # R$ 2500.50
    
    # Formatação de data
    data = datetime.now()
    data_formatada = format_date(data, DATE_FORMATS['DISPLAY'])
    print(f"Data formatada: {data_formatada}")  # 25/12/2024
    
    # Construção de endereço
    endereco = build_address(
        rua="Rua das Flores",
        bairro="Centro",
        cidade="São Paulo",
        estado="SP",
        cep="01234-567"
    )
    print(f"Endereço completo: {endereco}")
    # Rua das Flores, Centro, São Paulo - SP, CEP: 01234-567


def exemplo_validacao_arquivos():
    """Exemplo de validação de arquivos"""
    
    # Validação de extensão
    arquivo_valido = "contrato.pdf"
    arquivo_invalido = "contrato.doc"
    
    print(f"Arquivo válido: {validate_file_extension(arquivo_valido, ALLOWED_FILE_EXTENSIONS)}")  # True
    print(f"Arquivo inválido: {validate_file_extension(arquivo_invalido, ALLOWED_FILE_EXTENSIONS)}")  # False
    
    # Sanitização de nome de arquivo
    nome_sujo = "Contrato<>:\"/\\|?*.pdf"
    nome_limpo = sanitize_filename(nome_sujo)
    print(f"Nome limpo: {nome_limpo}")  # Contrato_____.pdf
    
    # Criação de nome único
    nome_unico = create_unique_filename("contrato_entrada_joao_silva", ".pdf")
    print(f"Nome único: {nome_unico}")  # contrato_entrada_joao_silva_20241225143022.pdf


def exemplo_constantes():
    """Exemplo de uso das constantes"""
    
    # Tipos de contrato
    print(f"Tipos de contrato disponíveis: {list(CONTRACT_TYPES.values())}")
    # ['contrato_entrada', 'termo_uso', 'sindicato']
    
    # Status de contratos
    print(f"Status disponíveis: {list(CONTRACT_STATUS.values())}")
    # ['aguardando assinatura', 'assinado']
    
    # Estados brasileiros
    print(f"Total de estados: {len(BRAZILIAN_STATES)}")  # 27
    
    # Mensagens
    print(f"Mensagem de sucesso: {MESSAGES['CONTRACT_SIGNED_SUCCESS']}")
    # Contrato assinado com sucesso!
    
    # Valores padrão
    print(f"Carga horária padrão: {DEFAULT_VALUES['CARGA_HORARIA']}")  # 40


def exemplo_extracao_tipo_contrato():
    """Exemplo de extração do tipo de contrato do nome do arquivo"""
    
    arquivos = [
        "contrato_entrada_joao_silva_20241225.pdf",
        "termo_uso_maria_santos_20241225.pdf",
        "sindicato_pedro_oliveira_20241225.pdf",
        "outro_arquivo.pdf"
    ]
    
    for arquivo in arquivos:
        tipo = get_contract_type_from_filename(arquivo)
        print(f"Arquivo: {arquivo} -> Tipo: {tipo}")


def exemplo_operacoes_arquivo():
    """Exemplo de operações seguras com arquivos"""
    
    # Garantir que diretório existe
    diretorio = "/tmp/exemplo_uploads"
    ensure_directory_exists(diretorio)
    print(f"Diretório criado/verificado: {diretorio}")


def exemplo_uso_completo():
    """Exemplo completo de uso das funcionalidades"""
    
    print("=== Exemplo Completo de Uso ===")
    
    # 1. Formatação de dados
    print("\n1. Formatação de dados:")
    exemplo_formatacao_dados()
    
    # 2. Validação de arquivos
    print("\n2. Validação de arquivos:")
    exemplo_validacao_arquivos()
    
    # 3. Uso de constantes
    print("\n3. Uso de constantes:")
    exemplo_constantes()
    
    # 4. Extração de tipo de contrato
    print("\n4. Extração de tipo de contrato:")
    exemplo_extracao_tipo_contrato()
    
    # 5. Operações de arquivo
    print("\n5. Operações de arquivo:")
    exemplo_operacoes_arquivo()


if __name__ == "__main__":
    exemplo_uso_completo()
