"""
Controllers for employee management
"""

import json
from datetime import datetime
from py4web import URL, action, redirect, request, response
from py4web.utils.form import Form, FormStyleBootstrap4

from ..common import T, auth, authenticated, cache, db, flash, logger, session
from ..config import SEARCH_CONFIG
from ..constants import DATE_FORMATS


@action('index', method=['GET', 'POST'])
@action.uses('index.html', auth.user)
def index():
    """Main application index page"""
    return dict()


@action('buscar_funcionario')
@action.uses(db)
def buscar_funcionario():
    """Search employees via AJAX"""
    query = request.query.get('q', '').strip()
    if not query or len(query) < SEARCH_CONFIG['min_query_length']:
        return json.dumps([])
    
    logger.info(f'Searching employees with query: {query}')
    
    try:
        # Use more efficient Pydal query
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
        
        logger.info(f'Found {len(funcionarios)} employees')
        
        return json.dumps([{
            'id': f.id,
            'nome': f.nome
        } for f in funcionarios])
    except Exception as e:
        logger.error(f'Error searching employees: {str(e)}')
        return json.dumps([])


@action("cadastrar_funcionario")
@action.uses(db, auth, "cadastrar_funcionario.html")
def cadastrar_funcionario():
    """Employee registration form"""
    form = Form(db.funcionario)
    return dict(form=form)


@action('listar_funcionarios')
@action.uses(db, auth)
def listar_funcionarios():
    """List all employees as JSON"""
    try:
        # Get all employees
        funcionarios = db(db.funcionario).select()
        
        # Convert to dictionary and format dates
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
                'data_nascimento': f.data_nascimento.strftime(DATE_FORMATS['DISPLAY']) if f.data_nascimento else None,
                'rua': f.rua,
                'bairro': f.bairro,
                'cidade': f.cidade,
                'cep': f.cep,
                'estado': f.estado,
                'data_entrada': f.data_entrada.strftime(DATE_FORMATS['DISPLAY']) if f.data_entrada else None,
                'cargo': f.cargo,
                'salario': float(f.salario) if f.salario else None
            }
            funcionarios_list.append(funcionario_dict)
        
        return json.dumps(funcionarios_list)
    except Exception as e:
        logger.error(f'Error listing employees: {str(e)}')
        return json.dumps([])


@action('funcionarios')
@action.uses('listar_funcionarios.html', auth.user)
def funcionarios():
    """Employee listing page"""
    return dict()


@action('funcionario/<id:int>')
@action.uses('funcionario_detalhe.html', db, auth.user)
def funcionario_detalhe(id=None):
    """Employee detail page"""
    funcionario = db.funcionario(id)
    if not funcionario:
        redirect(URL('funcionarios'))
    
    contratos = db(db.contrato.funcionario == id).select(orderby=~db.contrato.data_geracao)
    return dict(funcionario=funcionario, contratos=contratos)


@action('funcionario/<id:int>/contratos')
@action.uses('contratos_funcionario.html', db, auth.user)
def contratos_funcionario(id=None):
    """Employee contracts page"""
    logger.info(f'Looking for contracts for employee ID: {id}')
    
    funcionario = db.funcionario(id)
    if not funcionario:
        logger.error(f'Employee not found with ID: {id}')
        redirect(URL('funcionarios'))
    
    logger.info(f'Employee found - ID: {funcionario.id}, Name: {funcionario.nome}')
    
    contratos = db(db.contrato.funcionario == id).select(orderby=~db.contrato.data_geracao)
    logger.info(f'Found {len(contratos)} contracts for the employee')
    
    for contrato in contratos:
        logger.debug(f'  Contract ID: {contrato.id}, Status: {contrato.status}, File: {contrato.arquivo}, Signed File: {contrato.arquivo_assinado}')
    
    return dict(funcionario=funcionario, contratos=contratos) 