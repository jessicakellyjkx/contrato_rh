"""
Controllers for file uploads and debugging
"""

import json
import os
import urllib.parse
from py4web import action, response

from ..common import db, auth, logger
from .. import settings


@action('uploads/<filename>')
def uploads(filename):
    """Serve uploaded files"""
    logger.info(f'DEBUG: filename received: {filename}')
    
    # Decode filename from URL
    filename_decoded = urllib.parse.unquote(filename)
    logger.info(f'DEBUG: decoded filename: {filename_decoded}')
    
    # Check if file exists in contract.arquivo table
    row = db(db.contrato.arquivo == filename_decoded).select().first()
    if row:
        logger.info(f'DEBUG: Found in contract.arquivo: {row.arquivo}')
        logger.info(f'DEBUG: Contract ID: {row.id}')
        logger.info(f'DEBUG: Contract status: {row.status}')
        upload_path = os.path.join(settings.UPLOAD_FOLDER, filename_decoded)
        logger.info(f'DEBUG: File path: {upload_path}')
        logger.info(f'DEBUG: File exists? {os.path.exists(upload_path)}')
        if os.path.exists(upload_path):
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename="{filename_decoded}"'
            with open(upload_path, 'rb') as f:
                return f.read()
        return "Arquivo não encontrado no sistema de arquivos", 404
    
    # Check if file exists in contract.arquivo_assinado table
    row = db(db.contrato.arquivo_assinado == filename_decoded).select().first()
    if row:
        logger.info(f'DEBUG: Found in contract.arquivo_assinado: {row.arquivo_assinado}')
        logger.info(f'DEBUG: Contract ID: {row.id}')
        logger.info(f'DEBUG: Contract status: {row.status}')
        upload_path = os.path.join(settings.UPLOAD_FOLDER, filename_decoded)
        logger.info(f'DEBUG: File path: {upload_path}')
        logger.info(f'DEBUG: File exists? {os.path.exists(upload_path)}')
        if os.path.exists(upload_path):
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename="{filename_decoded}"'
            with open(upload_path, 'rb') as f:
                return f.read()
        return "Arquivo não encontrado no sistema de arquivos", 404
    
    # If not found, list all files for debug
    logger.error('DEBUG: File not found in database')
    logger.info('DEBUG: Listing all contracts for debug:')
    todos_contratos = db(db.contrato).select()
    for contrato in todos_contratos:
        logger.info(f'  Contract ID: {contrato.id}, File: {contrato.arquivo}, Signed File: {contrato.arquivo_assinado}, Status: {contrato.status}')
    
    return "Arquivo não encontrado", 404


@action('debug_contratos')
@action.uses(db, auth.user)
def debug_contratos():
    """Debug function to check database state"""
    logger.info("=== DEBUG: Database state ===")
    
    # Check all employees
    funcionarios = db(db.funcionario).select()
    logger.info(f"Total employees: {len(funcionarios)}")
    for f in funcionarios:
        logger.info(f"  Employee ID: {f.id}, Name: {f.nome}")
    
    # Check all contracts
    contratos = db(db.contrato).select()
    logger.info(f"Total contracts: {len(contratos)}")
    for c in contratos:
        logger.info(f"  Contract ID: {c.id}, Employee: {c.funcionario}, Status: {c.status}")
        logger.info(f"    File: {c.arquivo}")
        logger.info(f"    Signed File: {c.arquivo_assinado}")
        logger.info(f"    Generation Date: {c.data_geracao}")
        logger.info(f"    Signature Date: {c.data_assinatura}")
    
    return "Debug complete. Check server logs."


@action('test_json_response')
@action.uses(db, auth.user)
def test_json_response():
    """Test JSON response function"""
    logger.info('DEBUG: Testing JSON response')
    
    try:
        response.headers['Content-Type'] = 'application/json'
        return json.dumps(dict(success=True, message='JSON test working!'))
    except Exception as e:
        logger.error(f'DEBUG: JSON test error: {str(e)}')
        import traceback
        logger.error(f'DEBUG: Traceback: {traceback.format_exc()}')
        return "JSON test error"
