"""
Controllers for contract management
"""

import json
import os
import tempfile
from datetime import datetime
from py4web import URL, action, redirect, request, response
from py4web.utils.form import Form, FormStyleBootstrap4
import pdfkit

from ..common import T, auth, authenticated, cache, db, flash, logger, session
from ..config import PDF_CONFIG, EMPRESA_CONFIG, UPLOAD_CONFIG
from ..constants import (
    CONTRACT_TYPES, CONTRACT_STATUS, DEFAULT_VALUES, MESSAGES,
    DATE_FORMATS, ALLOWED_FILE_EXTENSIONS
)
from .. import settings
from ..utils import (
    sanitize_filename, format_currency, format_date, build_address,
    get_contract_type_from_filename, validate_file_extension,
    validate_file_size, create_unique_filename, ensure_directory_exists
)


@action("gerar_contrato", method=['POST'])
@action.uses(db, auth, session, flash)
def gerar_contrato():
    """Generate contract PDF"""
    if not request.forms.get('id_funcionario') or not request.forms.get('tipo_contrato'):
        flash.set(MESSAGES['REQUIRED_FIELDS'])
        redirect(URL('index'))
    
    id_funcionario = request.forms.get('id_funcionario')
    tipo_contrato = request.forms.get('tipo_contrato')
    
    logger.info(f'Starting contract generation - ID: {id_funcionario}, Type: {tipo_contrato}')
    
    try:
        id_funcionario = int(id_funcionario)
        
        # Use select().first() for better performance
        funcionario = db.funcionario(id_funcionario)
        
        if not funcionario:
            logger.error(f'Employee not found with ID: {id_funcionario}')
            flash.set(MESSAGES['EMPLOYEE_NOT_FOUND'])
            redirect(URL('index'))
        
        logger.info(f'Employee found - ID: {funcionario.id}, Name: {funcionario.nome}')
        
        # Prepare data for template using centralized configurations
        dados = _prepare_contract_data(funcionario)
        
        # Get template path
        template_path = _get_template_path(tipo_contrato)
        
        if not os.path.exists(template_path):
            logger.error(f'Template not found: {template_path}')
            flash.set(MESSAGES['TEMPLATE_NOT_FOUND'])
            redirect(URL('index'))
        
        # Generate PDF
        pdf = _generate_pdf_from_template(template_path, dados)
        
        # Save file and register contract
        nome_arquivo = _save_contract_file(pdf, funcionario, tipo_contrato)
        _register_contract(funcionario.id, nome_arquivo)
        
        # Configure headers for download
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={nome_arquivo}'
        
        return pdf
        
    except ValueError:
        logger.error(f'Invalid ID: {id_funcionario}')
        flash.set(MESSAGES['INVALID_EMPLOYEE_ID'])
        redirect(URL('index'))
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        flash.set(MESSAGES['PROCESSING_ERROR'])
        redirect(URL('index'))


@action('assinar_contrato/<contrato_id:int>', method=['GET', 'POST'])
@action.uses(db, auth.user, 'assinar_contrato.html')
def assinar_contrato(contrato_id=None):
    """Contract signing form"""
    contrato = db.contrato(contrato_id)
    if not contrato:
        redirect(URL('funcionarios'))
    
    # Use model field for upload
    form = Form(
        db.contrato,
        record=contrato,
        fields=['arquivo_assinado'],
        deletable=False,
        formstyle=FormStyleBootstrap4
    )
    
    if form.accepted:
        # Update contract status
        contrato.update_record(
            arquivo_assinado=form.vars.arquivo_assinado,
            status=CONTRACT_STATUS['ASSINADO'],
            data_assinatura=datetime.now()
        )
        db.commit()
        flash.set(MESSAGES['CONTRACT_SIGNED_SUCCESS'])
        redirect(URL('funcionario', contrato.funcionario, 'contratos'))
    
    return dict(form=form, contrato=contrato, funcionario=db.funcionario(contrato.funcionario))


@action('upload_contrato_assinado/<contrato_id:int>', method=['POST'])
@action.uses(db, auth.user)
def upload_contrato_assinado(contrato_id=None):
    """Upload signed contract via AJAX"""
    logger.info(f'Starting upload for contract ID: {contrato_id}')
    
    try:
        contrato = db.contrato(contrato_id)
        if not contrato:
            logger.error(f'Contract not found with ID: {contrato_id}')
            response.headers['Content-Type'] = 'application/json'
            return json.dumps(dict(success=False, message=MESSAGES['CONTRACT_NOT_FOUND']))
        
        logger.info(f'Contract found - ID: {contrato.id}, Status: {contrato.status}')
        
        # Check if file was sent
        if 'arquivo_assinado' not in request.files:
            logger.error('No file was sent')
            response.headers['Content-Type'] = 'application/json'
            return json.dumps(dict(success=False, message=MESSAGES['NO_FILE_SENT']))
        
        arquivo = request.files['arquivo_assinado']
        if not arquivo or not arquivo.filename:
            logger.error('Invalid file')
            response.headers['Content-Type'] = 'application/json'
            return json.dumps(dict(success=False, message=MESSAGES['INVALID_FILE']))
        
        logger.info(f'File received - Name: {arquivo.filename}')
        
        # Validate file
        if not _validate_uploaded_file(arquivo):
            response.headers['Content-Type'] = 'application/json'
            return json.dumps(dict(success=False, message=MESSAGES['FILE_TOO_LARGE']))
        
        # Save file
        nome_arquivo_assinado = _save_signed_contract_file(arquivo, contrato)
        
        # Update contract
        contrato.update_record(
            arquivo_assinado=nome_arquivo_assinado,
            status=CONTRACT_STATUS['ASSINADO'],
            data_assinatura=datetime.now()
        )
        db.commit()
        
        logger.info(f'Contract updated - Signed File: {nome_arquivo_assinado}, Status: assinado')
        
        response.headers['Content-Type'] = 'application/json'
        return json.dumps(dict(success=True, message=MESSAGES['CONTRACT_SIGNED_SUCCESS']))
        
    except Exception as e:
        logger.error(f'Error processing file: {str(e)}')
        import traceback
        logger.error(f'Complete traceback: {traceback.format_exc()}')
        response.headers['Content-Type'] = 'application/json'
        return json.dumps(dict(success=False, message=f'{MESSAGES["FILE_PROCESSING_ERROR"]}: {str(e)}'))


# Helper functions
def _prepare_contract_data(funcionario):
    """Prepare contract data from employee information"""
    return {
        'nome_empresa': EMPRESA_CONFIG['nome'],
        'cnpj': EMPRESA_CONFIG['cnpj'],      
        'endereco_empresa': EMPRESA_CONFIG['endereco'], 
        'nome_funcionario': funcionario.nome,
        'data_nascimento': format_date(funcionario.data_nascimento, DATE_FORMATS['DISPLAY']),
        'sexo': funcionario.sexo,
        'rg': funcionario.rg,
        'ctps': funcionario.ctps if hasattr(funcionario, 'ctps') else DEFAULT_VALUES['CTPS'],
        'cargo': funcionario.cargo,
        'carga_horaria': DEFAULT_VALUES['CARGA_HORARIA'],  
        'dias_semana': DEFAULT_VALUES['DIAS_SEMANA'],  
        'salario': format_currency(funcionario.salario),
        'data_inicio': format_date(funcionario.data_entrada, DATE_FORMATS['DISPLAY']),
        'cidade': funcionario.cidade,
        'data': format_date(datetime.now(), DATE_FORMATS['DISPLAY']),
        'cpf': funcionario.cpf,
        'estado_civil': funcionario.estado_civil,
        'endereco': build_address(funcionario.rua, funcionario.bairro, funcionario.cidade, funcionario.estado, funcionario.cep),
        'idade': funcionario.idade
    }


def _get_template_path(tipo_contrato):
    """Get template file path"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, '..', 'templates', 'contrato', f'{tipo_contrato}.html')


def _generate_pdf_from_template(template_path, dados):
    """Generate PDF from template with data"""
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Inline CSS to replace external references
    css_inline = _get_inline_css()
    
    # Replace external CSS reference with inline CSS
    template_content = template_content.replace(
        '<link rel="stylesheet" href="/myapp/static/css/contratos.css">',
        css_inline
    )
    
    # Replace variables in template
    for key, value in dados.items():
        template_content = template_content.replace(f'[{key}]', str(value))
    
    # Create temporary file with processed content
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as temp_file:
        temp_file.write(template_content)
        temp_file_path = temp_file.name
    
    try:
        # Configure wkhtmltopdf using centralized configurations
        config = pdfkit.configuration(wkhtmltopdf=PDF_CONFIG['wkhtmltopdf_path'])
        
        # PDF options
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
        
        # Generate PDF
        pdf = pdfkit.from_file(temp_file_path, False, configuration=config, options=options)
        return pdf
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def _get_inline_css():
    """Get inline CSS for contracts"""
    return """
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


def _save_contract_file(pdf, funcionario, tipo_contrato):
    """Save contract file and return filename"""
    nome_funcionario_limpo = sanitize_filename(funcionario.nome)
    nome_arquivo = create_unique_filename(f"{tipo_contrato}_{nome_funcionario_limpo}", ".pdf")
    
    # Ensure upload directory exists
    ensure_directory_exists(settings.UPLOAD_FOLDER)
    
    upload_path = os.path.join(settings.UPLOAD_FOLDER, nome_arquivo)
    with open(upload_path, 'wb') as f:
        f.write(pdf)
    
    return nome_arquivo


def _register_contract(funcionario_id, nome_arquivo):
    """Register contract in database"""
    contrato_id = db.contrato.insert(
        funcionario=funcionario_id,
        arquivo=nome_arquivo,
        status=CONTRACT_STATUS['AGUARDANDO_ASSINATURA'],
        data_geracao=datetime.now()
    )
    db.commit()
    return contrato_id


def _validate_uploaded_file(arquivo):
    """Validate uploaded file"""
    # Check file extension
    if not validate_file_extension(arquivo.filename, ALLOWED_FILE_EXTENSIONS):
        logger.error(f'Invalid file extension: {arquivo.filename}')
        return False
    
    # Check file size
    try:
        arquivo.file.seek(0, 2)  # Seek to end
        file_size = arquivo.file.tell()
        arquivo.file.seek(0)  # Reset to beginning
        
        if not validate_file_size(file_size, UPLOAD_CONFIG['max_file_size']):
            logger.error(f'File too large: {file_size} bytes')
            return False
    except Exception as e:
        logger.error(f'Error checking file size: {e}')
        return False
    
    return True


def _save_signed_contract_file(arquivo, contrato):
    """Save signed contract file and return filename"""
    # Get original contract type for filename
    tipo_contrato = get_contract_type_from_filename(contrato.arquivo)
    
    # Create clean filename for signed file
    nome_arquivo_assinado = create_unique_filename(f"{tipo_contrato}_assinado_{contrato.funcionario}", ".pdf")
    
    # Ensure upload directory exists
    ensure_directory_exists(settings.UPLOAD_FOLDER)
    
    # Save file using most compatible method
    upload_path = os.path.join(settings.UPLOAD_FOLDER, nome_arquivo_assinado)
    logger.info(f'Trying to save file at: {upload_path}')
    
    try:
        # Try using temporary file
        with open(upload_path, 'wb') as f:
            arquivo.file.seek(0)  # Go to beginning of file
            f.write(arquivo.file.read())
        logger.info(f'File saved using arquivo.file.read()')
    except Exception as e1:
        logger.error(f'Error with arquivo.file.read(): {e1}')
        try:
            # Try using content directly
            with open(upload_path, 'wb') as f:
                f.write(arquivo.value)
            logger.info(f'File saved using arquivo.value')
        except Exception as e2:
            logger.error(f'Error with arquivo.value: {e2}')
            # Last attempt: copy temporary file
            import shutil
            shutil.copy2(arquivo.file.name, upload_path)
            logger.info(f'File saved using shutil.copy2()')
    
    logger.info(f'File saved successfully: {nome_arquivo_assinado}')
    return nome_arquivo_assinado
