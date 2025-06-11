# Sistema de Gestão de Contratos RH

Sistema desenvolvido em Python utilizando Py4web para gerenciamento de contratos e informações de funcionários.

## Funcionalidades

- Cadastro de funcionários
- Listagem de funcionários
- Busca de funcionários
- Geração de contratos em PDF
- Visualização detalhada de funcionários

## Requisitos

- Python 3.8+
- wkhtmltopdf
- Py4web
- Outras dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/jessicakellyjkx/contrato_rh.git
cd contrato_rh
```

2. Crie um ambiente virtual Python:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Instale o wkhtmltopdf:
- Linux (Ubuntu/Debian):
```bash
sudo apt-get install wkhtmltopdf
```
- Windows: Baixe o instalador do [site oficial](https://wkhtmltopdf.org/downloads.html)

## Executando o Projeto

1. Ative o ambiente virtual (se ainda não estiver ativo):
```bash
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Inicie o servidor:
```bash
py4web run apps
```

3. Acesse o sistema em seu navegador:
```
http://localhost:8000/myapp
```

## Estrutura do Projeto

- `apps/myapp/` - Diretório principal da aplicação
  - `controllers.py` - Controladores da aplicação
  - `templates/` - Templates HTML
  - `models/` - Modelos de dados


