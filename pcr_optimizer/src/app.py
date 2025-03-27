"""
PCR Optimizer ana uygulama dosyası.
"""

import os
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import json
import tempfile
from datetime import datetime

from core.calculator import PCRCalculator
from core.optimizer import PCROptimizer
from core.protocol_generator import ProtocolGenerator
from utils.validators import PCRValidationError, validate_dna_sequence, validate_primer
from utils.validators import validate_template_length, validate_cycle_number, validate_concentration
from utils.helpers import format_dna_sequence, estimate_pcr_product_size, generate_filename


# Uygulama nesnesi oluşturma
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Flask flash mesajları için gerekli

# PCR bileşenleri oluşturma
calculator = PCRCalculator()
optimizer = PCROptimizer()
protocol_generator = ProtocolGenerator(optimizer)

# Geçici dosyalar için klasör
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'pcr_optimizer')
os.makedirs(TEMP_DIR, exist_ok=True)


@app.route('/')
def index():
    """Ana sayfa."""
    return render_template('index.html')


@app.route('/about')
def about():
    """Hakkında sayfası."""
    return render_template('about.html')


@app.route('/optimize', methods=['GET', 'POST'])
def optimize():
    """Optimizasyon sayfası."""
    if request.method == 'POST':
        try:
            # Form verilerini al
            data = {}
            
            # DNA uzunluğu veya dizisi
            if request.form.get('dna_sequence'):
                sequence = request.form.get('dna_sequence')
                try:
                    sequence = validate_dna_sequence(sequence)
                    data['sequence'] = sequence
                    # Uzunluğu otomatik hesapla
                    data['template_length'] = len(sequence)
                except PCRValidationError as e:
                    flash(str(e), 'error')
                    return render_template('optimize.html')
            elif request.form.get('template_length'):
                try:
                    template_length = validate_template_length(request.form.get('template_length'))
                    data['template_length'] = template_length
                except PCRValidationError as e:
                    flash(str(e), 'error')
                    return render_template('optimize.html')
            else:
                flash('DNA dizisi veya şablon uzunluğu girilmelidir.', 'error')
                return render_template('optimize.html')
                
            # Primer dizileri (opsiyonel)
            if request.form.get('forward_primer'):
                try:
                    forward_primer = validate_primer(
                        request.form.get('forward_primer'),
                        'İleri primer'
                    )
                    data['forward_primer'] = forward_primer
                except PCRValidationError as e:
                    flash(str(e), 'error')
                    return render_template('optimize.html')
                    
            if request.form.get('reverse_primer'):
                try:
                    reverse_primer = validate_primer(
                        request.form.get('reverse_primer'),
                        'Geri primer'
                    )
                    data['reverse_primer'] = reverse_primer
                except PCRValidationError as e:
                    flash(str(e), 'error')
                    return render_template('optimize.html')
            
            # Şablon konsantrasyonu (opsiyonel)
            if request.form.get('template_concentration'):
                try:
                    template_concentration = validate_concentration(
                        request.form.get('template_concentration'),
                        'Şablon konsantrasyonu'
                    )
                    data['template_concentration'] = template_concentration
                except PCRValidationError as e:
                    flash(str(e), 'error')
                    return render_template('optimize.html')
                    
            # Hedef verim (opsiyonel)
            if request.form.get('target_yield'):
                try:
                    target_yield = validate_concentration(
                        request.form.get('target_yield'),
                        'Hedef verim'
                    )
                    data['target_yield'] = target_yield
                except PCRValidationError as e:
                    flash(str(e), 'error')
                    return render_template('optimize.html')
                    
            # PCR tipi
            data['is_diagnostic'] = request.form.get('pcr_type') == 'diagnostic'
                
            # Protokolü oluştur
            protocol = protocol_generator.generate_protocol(**data)
            
            # Başarılı mesajı göster
            flash('PCR protokolü başarıyla oluşturuldu!', 'success')
            
            # Sesyon ID oluştur ve protokolü kaydet
            session_id = datetime.now().strftime('%Y%m%d%H%M%S')
            protocol_file = os.path.join(TEMP_DIR, f'protocol_{session_id}.json')
            with open(protocol_file, 'w', encoding='utf-8') as f:
                json.dump(protocol, f, ensure_ascii=False, indent=2)
                
            # Rapor sayfasına yönlendir
            return redirect(url_for('report', session_id=session_id))
            
        except Exception as e:
            flash(f'Beklenmeyen bir hata oluştu: {str(e)}', 'error')
            return render_template('optimize.html')
    
    # GET isteği
    return render_template('optimize.html')


@app.route('/report/<session_id>')
def report(session_id):
    """Rapor sayfası."""
    try:
        # Protokol dosyasını oku
        protocol_file = os.path.join(TEMP_DIR, f'protocol_{session_id}.json')
        with open(protocol_file, 'r', encoding='utf-8') as f:
            protocol = json.load(f)
            
        # Metinsel raporu oluştur
        report_text = protocol_generator.protocol_to_text(protocol)
        
        return render_template('report.html', 
                               protocol=protocol, 
                               report_text=report_text, 
                               session_id=session_id)
    except Exception as e:
        flash(f'Rapor yüklenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/download/<session_id>/<format>')
def download(session_id, format):
    """Protokol dosyası indirme."""
    try:
        # Protokol dosyasını oku
        protocol_file = os.path.join(TEMP_DIR, f'protocol_{session_id}.json')
        with open(protocol_file, 'r', encoding='utf-8') as f:
            protocol = json.load(f)
            
        # İstenen formatta rapor oluştur
        if format == 'json':
            content = protocol_generator.protocol_to_json(protocol)
            mimetype = 'application/json'
            filename = 'pcr_protocol.json'
        elif format == 'csv':
            content = protocol_generator.protocol_to_csv(protocol)
            mimetype = 'text/csv'
            filename = 'pcr_protocol.csv'
        else:  # text
            content = protocol_generator.protocol_to_text(protocol)
            mimetype = 'text/plain'
            filename = 'pcr_protocol.txt'
            
        # Geçici dosya oluştur
        temp_file = os.path.join(TEMP_DIR, generate_filename('pcr_protocol', format.lower()))
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Dosyayı gönder
        return send_file(temp_file, 
                         mimetype=mimetype,
                         as_attachment=True, 
                         download_name=filename)
    except Exception as e:
        flash(f'Dosya indirilirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/api/optimize', methods=['POST'])
def api_optimize():
    """PCR optimizasyon API."""
    try:
        # JSON verilerini al
        data = request.json
        
        # Veri doğrulama
        validated_data = {}
        
        # DNA dizisi veya uzunluğu
        if 'sequence' in data:
            validated_data['sequence'] = validate_dna_sequence(data['sequence'])
            validated_data['template_length'] = len(validated_data['sequence'])
        elif 'template_length' in data:
            validated_data['template_length'] = validate_template_length(data['template_length'])
        else:
            return jsonify({'error': 'DNA dizisi veya şablon uzunluğu gereklidir.'}), 400
            
        # Opsiyonel parametreler
        if 'forward_primer' in data:
            validated_data['forward_primer'] = validate_primer(data['forward_primer'], 'İleri primer')
            
        if 'reverse_primer' in data:
            validated_data['reverse_primer'] = validate_primer(data['reverse_primer'], 'Geri primer')
            
        if 'template_concentration' in data:
            validated_data['template_concentration'] = validate_concentration(
                data['template_concentration'], 
                'Şablon konsantrasyonu'
            )
            
        if 'target_yield' in data:
            validated_data['target_yield'] = validate_concentration(
                data['target_yield'], 
                'Hedef verim'
            )
            
        if 'is_diagnostic' in data:
            validated_data['is_diagnostic'] = bool(data['is_diagnostic'])
            
        # Protokolü oluştur
        protocol = protocol_generator.generate_protocol(**validated_data)
        
        # JSON yanıtı döndür
        return jsonify(protocol)
        
    except PCRValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Beklenmeyen bir hata oluştu: {str(e)}'}), 500


def create_app():
    """Flask uygulaması oluştur."""
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 