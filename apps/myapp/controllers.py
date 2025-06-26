"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from yatl.helpers import A, DIV, SPAN, I
import pdfkit
import os
from datetime import datetime
import tempfile
import json
from io import BytesIO
import urllib.parse

from py4web import URL, abort, action, redirect, request, response

from .common import (T, auth, authenticated, cache, db, flash, logger, session,
                     unauthenticated)

from py4web import action, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBootstrap4
from pydal.validators import *
from py4web.utils.downloader import downloader

# Importar configurações
from .config import PDF_CONFIG, EMPRESA_CONFIG, SEARCH_CONFIG

from . import settings

@action('index', method=['GET', 'POST'])
@action.uses('index.html', auth.user)
def index():
    return dict()

@action('buscar_funcionario')
@action.uses(db)
def buscar_funcionario():
    query = request.query.get('q', '').strip()
    if not query or len(query) < SEARCH_CONFIG['min_query_length']:
        return json.dumps([])
    
    logger.info(f'Buscando funcionários com query: {query}')
    
    try:
        # Usar query mais eficiente do Pydal
        if query.isdigit():
            id_query = int(query)
            funcionarios = db(
                (db.funcionario.id == id_query) |
                (db.funcionario.nome.contains(query))
            ).select(
                db.funcionario.id,
                db.funcionario.nome,
                limitby=(0, SEARCH_CONFIG['max_results'])
            )
        else:
            funcionarios = db(
                db.funcionario.nome.contains(query)
            ).select(
                db.funcionario.id,
                db.funcionario.nome,
                limitby=(0, SEARCH_CONFIG['max_results'])
            )
        
        logger.info(f'Encontrados {len(funcionarios)} funcionários')
        
        return json.dumps([{
            'id': f.id,
            'nome': f.nome
        } for f in funcionarios])
    except Exception as e:
        logger.error(f'Erro ao buscar funcionários: {str(e)}')
        return json.dumps([])

@action("gerar_contrato", method=['POST'])
@action.uses(db, auth, session, flash)
def gerar_contrato():
    if not request.forms.get('id_funcionario') or not request.forms.get('tipo_contrato'):
        flash.set('ID do funcionário e tipo de contrato são obrigatórios')
        redirect(URL('index'))
    
    id_funcionario = request.forms.get('id_funcionario')
    tipo_contrato = request.forms.get('tipo_contrato')
    
    logger.info(f'Iniciando geração de contrato - ID: {id_funcionario}, Tipo: {tipo_contrato}')
    
    try:
        id_funcionario = int(id_funcionario)
        
        # Usar select().first() para melhor performance
        funcionario = db.funcionario(id_funcionario)
        
        if not funcionario:
            logger.error(f'Funcionário não encontrado com ID: {id_funcionario}')
            flash.set('Funcionário não encontrado')
            redirect(URL('index'))
        
        logger.info(f'Funcionário encontrado - ID: {funcionario.id}, Nome: {funcionario.nome}')
        
        # Preparar dados para o template usando configurações centralizadas
        dados = {
            'nome_empresa': EMPRESA_CONFIG['nome'],
            'cnpj': EMPRESA_CONFIG['cnpj'],      
            'endereco_empresa': EMPRESA_CONFIG['endereco'], 
            'nome_funcionario': funcionario.nome,
            'data_nascimento': funcionario.data_nascimento.strftime('%d/%m/%Y') if funcionario.data_nascimento else '',
            'sexo': funcionario.sexo,
            'rg': funcionario.rg,
            'ctps': funcionario.ctps if hasattr(funcionario, 'ctps') else 'Nº da CTPS',
            'cargo': funcionario.cargo,
            'carga_horaria': '40',  
            'dias_semana': 'Segunda a Sexta',  
            'salario': f"R$ {funcionario.salario:.2f}" if funcionario.salario else '',
            'data_inicio': funcionario.data_entrada.strftime('%d/%m/%Y') if funcionario.data_entrada else '',
            'cidade': funcionario.cidade,
            'data': datetime.now().strftime('%d/%m/%Y'),
            'cpf': funcionario.cpf,
            'estado_civil': funcionario.estado_civil,
            'endereco': f"{funcionario.rua}, {funcionario.bairro}, {funcionario.cidade} - {funcionario.estado}, CEP: {funcionario.cep}" if funcionario.rua else '',
            'idade': funcionario.idade
        }
        
        # Obter o diretório atual do aplicativo
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, 'templates', 'contrato', f'{tipo_contrato}.html')
        
        logger.info(f'Diretório atual: {current_dir}')
        logger.info(f'Tentando abrir template: {template_path}')
        logger.info(f'Arquivo existe? {os.path.exists(template_path)}')
        
        if not os.path.exists(template_path):
            logger.error(f'Template não encontrado: {template_path}')
            flash.set('Template de contrato não encontrado')
            redirect(URL('index'))
        
        # Ler o template
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # CSS inline para substituir referências externas
        css_inline = """
        <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            color: #333;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h3 {
            color: #2c3e50;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }
        .contrato {
            max-width: 800px;
            margin: 0 auto;
        }
        .dados-pessoais {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .dados-pessoais p {
            margin: 5px 0;
        }
        .assinaturas {
            display: flex;
            justify-content: space-between;
            margin-top: 40px;
            margin-bottom: 20px;
        }
        .assinatura {
            text-align: center;
            width: 45%;
        }
        .assinatura strong {
            display: block;
            margin-top: 10px;
        }
        p {
            text-align: justify;
            margin-bottom: 15px;
        }
        strong {
            color: #2c3e50;
        }
        </style>
        """
        
        # Substituir referência ao CSS externo por CSS inline
        template_content = template_content.replace(
            '<link rel="stylesheet" href="/myapp/static/css/contratos.css">',
            css_inline
        )
        
        # Substituir as variáveis no template
        for key, value in dados.items():
            template_content = template_content.replace(f'[{key}]', str(value))
        
        # Criar arquivo temporário com o conteúdo processado
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as temp_file:
            temp_file.write(template_content)
            temp_file_path = temp_file.name
        
        try:
            # Configurar wkhtmltopdf usando configurações centralizadas
            config = pdfkit.configuration(wkhtmltopdf=PDF_CONFIG['wkhtmltopdf_path'])
            
            # Opções do PDF
            options = {
                'page-size': PDF_CONFIG['page_size'],
                'orientation': PDF_CONFIG['orientation'],
                'margin-top': PDF_CONFIG['margin_top'],
                'margin-right': PDF_CONFIG['margin_right'],
                'margin-bottom': PDF_CONFIG['margin_bottom'],
                'margin-left': PDF_CONFIG['margin_left'],
                'encoding': 'UTF-8',
                'no-outline': None,
                'disable-smart-shrinking': None,
                'print-media-type': None,
                'no-images': None,
                'disable-external-links': None,
                'disable-internal-links': None
            }
            
            # Gerar PDF
            pdf = pdfkit.from_file(temp_file_path, False, configuration=config, options=options)

            # Usar o sistema de uploads do Py4web
            # Criar nome do arquivo com tipo de contrato e nome do funcionário
            nome_funcionario_limpo = funcionario.nome.replace(' ', '_').replace('/', '_').replace('\\', '_')
            nome_arquivo = f"{tipo_contrato}_{nome_funcionario_limpo}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            
            # Salvar o arquivo diretamente no sistema de arquivos
            upload_path = os.path.join(settings.UPLOAD_FOLDER, nome_arquivo)
            with open(upload_path, 'wb') as f:
                f.write(pdf)
            
            # Registrar contrato no banco com o nome do arquivo
            contrato_id = db.contrato.insert(
                funcionario=funcionario.id,
                arquivo=nome_arquivo,
                status='aguardando assinatura',
                data_geracao=datetime.now()
            )
            db.commit()

            # Configurar headers para download
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={nome_arquivo}'
            
            return pdf
        except Exception as e:
            logger.error(f'Erro ao gerar PDF: {str(e)}')
            flash.set(f'Erro ao gerar PDF: {str(e)}')
            redirect(URL('index'))
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except ValueError:
        logger.error(f'ID inválido: {id_funcionario}')
        flash.set('ID do funcionário inválido')
        redirect(URL('index'))
    except Exception as e:
        logger.error(f'Erro inesperado: {str(e)}')
        flash.set('Erro ao processar a requisição')
        redirect(URL('index'))

@action("cadastrar_funcionario")
@action.uses(db, auth, "cadastrar_funcionario.html")
def cadastrar_funcionario():
    form = Form(db.funcionario)
    return dict(form=form)

@action('listar_funcionarios')
@action.uses(db, auth)
def listar_funcionarios():
    # Buscar todos os funcionários
    funcionarios = db(db.funcionario).select()
    
    # Converter para dicionário e formatar datas
    funcionarios_list = []
    for f in funcionarios:
        funcionario_dict = {
            'id': f.id,
            'nome': f.nome,
            'cpf': f.cpf,
            'rg': f.rg,
            'idade': f.idade,
            'estado_civil': f.estado_civil,
            'sexo': f.sexo,
            'data_nascimento': f.data_nascimento.strftime('%d/%m/%Y') if f.data_nascimento else None,
            'rua': f.rua,
            'bairro': f.bairro,
            'cidade': f.cidade,
            'cep': f.cep,
            'estado': f.estado,
            'data_entrada': f.data_entrada.strftime('%d/%m/%Y') if f.data_entrada else None,
            'cargo': f.cargo,
            'salario': float(f.salario) if f.salario else None
        }
        funcionarios_list.append(funcionario_dict)
    
    return json.dumps(funcionarios_list)

@action('funcionarios')
@action.uses('listar_funcionarios.html', auth.user)
def funcionarios():
    return dict()

@action('funcionario/<id:int>')
@action.uses('funcionario_detalhe.html', db, auth.user)
def funcionario_detalhe(id=None):
    funcionario = db.funcionario(id)
    if not funcionario:
        redirect(URL('funcionarios'))
    contratos = db(db.contrato.funcionario == id).select(orderby=~db.contrato.data_geracao)
    return dict(funcionario=funcionario, contratos=contratos)

@action('funcionario/<id:int>/contratos')
@action.uses('contratos_funcionario.html', db, auth.user)
def contratos_funcionario(id=None):
    print(f'DEBUG: Buscando contratos para funcionário ID: {id}')
    
    funcionario = db.funcionario(id)
    if not funcionario:
        print(f'DEBUG: Funcionário não encontrado com ID: {id}')
        redirect(URL('funcionarios'))
    
    print(f'DEBUG: Funcionário encontrado - ID: {funcionario.id}, Nome: {funcionario.nome}')
    
    contratos = db(db.contrato.funcionario == id).select(orderby=~db.contrato.data_geracao)
    print(f'DEBUG: Encontrados {len(contratos)} contratos para o funcionário')
    
    for contrato in contratos:
        print(f'  Contrato ID: {contrato.id}, Status: {contrato.status}, Arquivo: {contrato.arquivo}, Arquivo Assinado: {contrato.arquivo_assinado}')
    
    return dict(funcionario=funcionario, contratos=contratos)

# Usar o sistema de uploads integrado do Py4web
@action('uploads/<filename>')
def uploads(filename):
    import urllib.parse
    import os
    
    print('DEBUG: filename recebido:', filename)
    
    # Decodificar o nome do arquivo da URL
    filename_decoded = urllib.parse.unquote(filename)
    print('DEBUG: filename decodificado:', filename_decoded)
    
    # Verificar se o arquivo existe na tabela contrato.arquivo
    row = db(db.contrato.arquivo == filename_decoded).select().first()
    if row:
        print('DEBUG: Encontrado em contrato.arquivo:', row.arquivo)
        print('DEBUG: ID do contrato:', row.id)
        print('DEBUG: Status do contrato:', row.status)
        upload_path = os.path.join(settings.UPLOAD_FOLDER, filename_decoded)
        print('DEBUG: Caminho do arquivo:', upload_path)
        print('DEBUG: Arquivo existe?', os.path.exists(upload_path))
        if os.path.exists(upload_path):
            from py4web import response
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename="{filename_decoded}"'
            with open(upload_path, 'rb') as f:
                return f.read()
        return "Arquivo não encontrado no sistema de arquivos", 404
    
    # Verificar se o arquivo existe na tabela contrato.arquivo_assinado
    row = db(db.contrato.arquivo_assinado == filename_decoded).select().first()
    if row:
        print('DEBUG: Encontrado em contrato.arquivo_assinado:', row.arquivo_assinado)
        print('DEBUG: ID do contrato:', row.id)
        print('DEBUG: Status do contrato:', row.status)
        upload_path = os.path.join(settings.UPLOAD_FOLDER, filename_decoded)
        print('DEBUG: Caminho do arquivo:', upload_path)
        print('DEBUG: Arquivo existe?', os.path.exists(upload_path))
        if os.path.exists(upload_path):
            from py4web import response
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename="{filename_decoded}"'
            with open(upload_path, 'rb') as f:
                return f.read()
        return "Arquivo não encontrado no sistema de arquivos", 404
    
    # Se não encontrou, vamos listar todos os arquivos para debug
    print('DEBUG: Arquivo não encontrado no banco')
    print('DEBUG: Listando todos os contratos para debug:')
    todos_contratos = db(db.contrato).select()
    for contrato in todos_contratos:
        print(f'  Contrato ID: {contrato.id}, Arquivo: {contrato.arquivo}, Arquivo Assinado: {contrato.arquivo_assinado}, Status: {contrato.status}')
    
    return "Arquivo não encontrado", 404

# Criar formulário automático para assinatura de contrato
@action('assinar_contrato/<contrato_id:int>', method=['GET', 'POST'])
@action.uses(db, auth.user, 'assinar_contrato.html')
def assinar_contrato(contrato_id=None):
    contrato = db.contrato(contrato_id)
    if not contrato:
        redirect(URL('funcionarios'))
    
    # Usar o campo do modelo para upload
    form = Form(
        db.contrato,
        record=contrato,
        fields=['arquivo_assinado'],
        deletable=False,
        formstyle=FormStyleBootstrap4
    )
    
    if form.accepted:
        # Atualizar status do contrato
        contrato.update_record(
            arquivo_assinado=form.vars.arquivo_assinado,
            status='assinado',
            data_assinatura=datetime.now()
        )
        db.commit()
        flash.set('Contrato assinado com sucesso!')
        redirect(URL('funcionario', contrato.funcionario, 'contratos'))
    
    return dict(form=form, contrato=contrato, funcionario=db.funcionario(contrato.funcionario))

# Nova função para upload via AJAX
@action('upload_contrato_assinado/<contrato_id:int>', method=['POST'])
@action.uses(db, auth.user)
def upload_contrato_assinado(contrato_id=None):
    print(f'DEBUG: Iniciando upload para contrato ID: {contrato_id}')
    
    contrato = db.contrato(contrato_id)
    if not contrato:
        print(f'DEBUG: Contrato não encontrado com ID: {contrato_id}')
        return response.json(dict(success=False, message='Contrato não encontrado'))
    
    print(f'DEBUG: Contrato encontrado - ID: {contrato.id}, Status: {contrato.status}')
    
    try:
        # Verificar se foi enviado um arquivo
        if 'arquivo_assinado' not in request.files:
            print('DEBUG: Nenhum arquivo foi enviado')
            return response.json(dict(success=False, message='Nenhum arquivo foi enviado'))
        
        arquivo = request.files['arquivo_assinado']
        if not arquivo or not arquivo.filename:
            print('DEBUG: Arquivo inválido')
            return response.json(dict(success=False, message='Arquivo inválido'))
        
        print(f'DEBUG: Arquivo recebido - Nome: {arquivo.filename}, Tamanho: {len(arquivo.read())}')
        arquivo.seek(0)  # Voltar ao início do arquivo
        
        # Buscar o tipo de contrato original para incluir no nome
        contrato_original = db.contrato(contrato_id)
        tipo_contrato = "contrato_entrada"  # padrão
        if contrato_original and contrato_original.arquivo:
            # Extrair tipo do nome do arquivo original
            nome_original = contrato_original.arquivo
            if nome_original.startswith("contrato_entrada_"):
                tipo_contrato = "contrato_entrada"
            elif nome_original.startswith("termo_uso_"):
                tipo_contrato = "termo_uso"
            elif nome_original.startswith("sindicato_"):
                tipo_contrato = "sindicato"
        
        # Criar nome limpo para o arquivo assinado
        nome_arquivo_assinado = f"{tipo_contrato}_assinado_{contrato.funcionario}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        
        # Salvar o arquivo diretamente no sistema de arquivos
        upload_path = os.path.join(settings.UPLOAD_FOLDER, nome_arquivo_assinado)
        with open(upload_path, 'wb') as f:
            f.write(arquivo.read())
        
        # Atualizar o contrato
        contrato.update_record(
            arquivo_assinado=nome_arquivo_assinado,
            status='assinado',
            data_assinatura=datetime.now()
        )
        db.commit()
        
        print(f'DEBUG: Contrato atualizado - Arquivo Assinado: {nome_arquivo_assinado}, Status: assinado')
        
        return response.json(dict(success=True, message='Contrato assinado com sucesso!'))
        
    except Exception as e:
        print(f'DEBUG: Erro ao processar arquivo: {str(e)}')
        return response.json(dict(success=False, message=f'Erro ao processar arquivo: {str(e)}'))
    
# Função de debug para verificar o estado do banco
@action('debug_contratos')
@action.uses(db, auth.user)
def debug_contratos():
    print("=== DEBUG: Estado do banco de dados ===")
    
    # Verificar todos os funcionários
    funcionarios = db(db.funcionario).select()
    print(f"Total de funcionários: {len(funcionarios)}")
    for f in funcionarios:
        print(f"  Funcionário ID: {f.id}, Nome: {f.nome}")
    
    # Verificar todos os contratos
    contratos = db(db.contrato).select()
    print(f"Total de contratos: {len(contratos)}")
    for c in contratos:
        print(f"  Contrato ID: {c.id}, Funcionário: {c.funcionario}, Status: {c.status}")
        print(f"    Arquivo: {c.arquivo}")
        print(f"    Arquivo Assinado: {c.arquivo_assinado}")
        print(f"    Data Geração: {c.data_geracao}")
        print(f"    Data Assinatura: {c.data_assinatura}")
    
    return "Debug completo. Verifique os logs do servidor."
    
