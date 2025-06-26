# Sistema de Contratos RH - Py4web

Sistema de gerenciamento de contratos de recursos humanos desenvolvido com Py4web.

## Estrutura do Projeto

```
apps/myapp/
├── controllers/           # Controllers organizados por funcionalidade
│   ├── __init__.py       # Importa todos os controllers
│   ├── funcionarios.py   # Gestão de funcionários
│   ├── contratos.py      # Gestão de contratos
│   └── uploads.py        # Upload e download de arquivos
├── models.py             # Modelos de dados
├── config.py             # Configurações do aplicativo
├── constants.py          # Constantes centralizadas
├── utils.py              # Funções utilitárias
├── settings.py           # Configurações do Py4web
├── common.py             # Configurações comuns
├── templates/            # Templates HTML
├── static/               # Arquivos estáticos
└── uploads/              # Arquivos enviados
```

## Organização do Código

### 1. Controllers (`controllers/`)

Os controllers foram divididos por funcionalidade:

- **`funcionarios.py`**: Gestão de funcionários (CRUD, busca, listagem)
- **`contratos.py`**: Geração e assinatura de contratos
- **`uploads.py`**: Servir arquivos e funções de debug

### 2. Modelos (`models.py`)

Definição das tabelas do banco de dados com validações centralizadas usando constantes.

### 3. Configurações (`config.py`)

Configurações organizadas por categoria:
- `PDF_CONFIG`: Configurações para geração de PDF
- `EMPRESA_CONFIG`: Dados da empresa
- `UPLOAD_CONFIG`: Configurações de upload
- `SEARCH_CONFIG`: Configurações de busca
- `PAGINATION_CONFIG`: Configurações de paginação
- `CACHE_CONFIG`: Configurações de cache
- `LOGGING_CONFIG`: Configurações de log

### 4. Constantes (`constants.py`)

Valores fixos centralizados:
- Tipos de contrato
- Status de contratos
- Estados brasileiros
- Opções de estado civil e gênero
- Mensagens de erro/sucesso
- Padrões de validação
- Formatos de data
- Classes CSS

### 5. Utilitários (`utils.py`)

Funções auxiliares reutilizáveis:
- Formatação de dados (moeda, data, endereço)
- Validação de arquivos
- Sanitização de nomes de arquivo
- Operações seguras de arquivo

## Melhorias Implementadas

### 1. Separação de Responsabilidades
- Cada controller tem uma responsabilidade específica
- Funções auxiliares separadas dos controllers principais
- Configurações centralizadas

### 2. Reutilização de Código
- Funções utilitárias compartilhadas
- Constantes centralizadas
- Configurações reutilizáveis

### 3. Manutenibilidade
- Código mais limpo e organizado
- Documentação clara
- Fácil localização de funcionalidades

### 4. Validação e Segurança
- Validação de arquivos centralizada
- Sanitização de nomes de arquivo
- Tratamento de erros consistente

### 5. Performance
- Queries otimizadas
- Índices de banco de dados
- Configurações de cache

## Como Usar

### 1. Configuração Inicial

Edite o arquivo `config.py` com as configurações da sua empresa:

```python
EMPRESA_CONFIG = {
    'nome': 'Nome da Sua Empresa',
    'cnpj': '00.000.000/0000-00',
    'endereco': 'Endereço da Sua Empresa',
    # ...
}
```

### 2. Configuração do PDF

Certifique-se de que o wkhtmltopdf está instalado e configurado:

```python
PDF_CONFIG = {
    'wkhtmltopdf_path': '/usr/bin/wkhtmltopdf',  # Ajuste o caminho
    # ...
}
```

### 3. Execução

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o servidor
py4web run apps
```

## Funcionalidades

### Gestão de Funcionários
- Cadastro de funcionários
- Busca por nome ou ID
- Listagem de funcionários
- Detalhes do funcionário

### Gestão de Contratos
- Geração de contratos em PDF
- Assinatura digital de contratos
- Upload de contratos assinados
- Histórico de contratos por funcionário

### Tipos de Contrato
- Contrato de entrada
- Termo de uso
- Contrato sindical

## Estrutura de Dados

### Tabela `funcionario`
- Dados pessoais (nome, CPF, RG, etc.)
- Endereço completo
- Informações profissionais (cargo, salário, etc.)
- Campos de auditoria (created_on, updated_on)

### Tabela `contrato`
- Referência ao funcionário
- Arquivo do contrato original
- Status do contrato
- Arquivo assinado (quando aplicável)
- Datas de geração e assinatura

## Logs e Debug

O sistema inclui logs detalhados para facilitar o debug:
- Logs de busca de funcionários
- Logs de geração de contratos
- Logs de upload de arquivos
- Função de debug para verificar estado do banco

## Segurança

- Validação de tipos de arquivo
- Limite de tamanho de arquivo
- Sanitização de nomes de arquivo
- Autenticação requerida para ações sensíveis
- Validação de dados de entrada

## Contribuição

Para contribuir com o projeto:

1. Mantenha a organização de arquivos
2. Use as constantes centralizadas
3. Adicione documentação para novas funcionalidades
4. Implemente validações adequadas
5. Adicione logs para debug 