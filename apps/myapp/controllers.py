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

from yatl.helpers import A
import pdfkit
import os
from datetime import datetime
import tempfile
import json

from py4web import URL, abort, action, redirect, request, response

from .common import (T, auth, authenticated, cache, db, flash, logger, session,
                     unauthenticated)

from py4web import action, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBootstrap4
from pydal.validators import *

@action('index', method=['GET', 'POST'])
@action.uses('index.html', auth.user)
def index():
    return dict()

@action('buscar_funcionario')
@action.uses(db)
def buscar_funcionario():
    query = request.query.get('q', '').strip()
    if not query:
        return json.dumps([])
    
    logger.info(f'Buscando funcionários com query: {query}')
    
    try:
        # Tentar converter para inteiro se for um ID
        if query.isdigit():
            id_query = int(query)
            funcionarios = db(
                (db.funcionario.id == id_query) |
                (db.funcionario.nome.contains(query))
            ).select(
                db.funcionario.id,
                db.funcionario.nome,
                limitby=(0, 10)
            )
        else:
            # Se não for um número, buscar apenas por nome
            funcionarios = db(
                db.funcionario.nome.contains(query)
            ).select(
                db.funcionario.id,
                db.funcionario.nome,
                limitby=(0, 10)
            )
        
        logger.info(f'Encontrados {len(funcionarios)} funcionários')
        for f in funcionarios:
            logger.info(f'Funcionário encontrado - ID: {f.id}, Nome: {f.nome}')
        
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
        # Converter ID para inteiro
        id_funcionario = int(id_funcionario)
        
        # Buscar dados do funcionário
        funcionario = db(db.funcionario.id == id_funcionario).select().first()
        
        if not funcionario:
            logger.error(f'Funcionário não encontrado com ID: {id_funcionario}')
            flash.set('Funcionário não encontrado')
            redirect(URL('index'))
        
        logger.info(f'Funcionário encontrado - ID: {funcionario.id}, Nome: {funcionario.nome}')
        
        # Preparar dados para o template
        dados = {
            'nome_empresa': 'Nome da Empresa',  # Substitua pelo nome real da empresa
            'cnpj': '00.000.000/0000-00',      # Substitua pelo CNPJ real
            'endereco_empresa': 'Endereço da Empresa',  # Substitua pelo endereço real
            'nome_funcionario': funcionario.nome,
            'data_nascimento': funcionario.data_nascicmento.strftime('%d/%m/%Y') if funcionario.data_nascicmento else '',
            'sexo': funcionario.sexo,
            'rg': funcionario.rg,
            'ctps': funcionario.ctps if hasattr(funcionario, 'ctps') else 'Nº da CTPS',
            'cargo': funcionario.cargo,
            'carga_horaria': '40',  # Ajuste conforme necessário
            'dias_semana': 'Segunda a Sexta',  # Ajuste conforme necessário
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
        
        # Substituir as variáveis no template
        for key, value in dados.items():
            template_content = template_content.replace(f'[{key}]', str(value))
        
        # Criar arquivo temporário com o conteúdo processado
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as temp_file:
            temp_file.write(template_content)
            temp_file_path = temp_file.name
        
        try:
            # Configurar wkhtmltopdf
            config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
            
            # Gerar PDF
            pdf = pdfkit.from_file(temp_file_path, False, configuration=config)
            
            # Configurar headers para download
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=contrato_{funcionario.nome}.pdf'
            
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
            'data_nascicmento': f.data_nascicmento.strftime('%d/%m/%Y') if f.data_nascicmento else None,
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
    funcionario = db(db.funcionario.id == id).select().first()
    if not funcionario:
        redirect(URL('funcionarios'))
    return dict(funcionario=funcionario)
    
