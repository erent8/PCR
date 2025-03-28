"""
PCR Optimizer Web Uygulaması - Flask Backend
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Modül import yollarını düzenleme
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from core.calculator import PCRCalculator
from core.optimizer import PCROptimizer
from core.protocol_generator import PCRProtocolGenerator
from core.primer_designer import PrimerDesigner

# Uygulama yapılandırması
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'fasta', 'fa', 'txt', 'seq'}
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB max dosya boyutu

# Klasör oluşturma
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# PCR bileşenleri oluştur
calculator = PCRCalculator()
optimizer = PCROptimizer()
protocol_generator = PCRProtocolGenerator()
primer_designer = PrimerDesigner()

# Loglama
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Yüklenen dosya izin verilen bir uzantıya sahip mi kontrol eder."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Ana sayfa."""
    return render_template('index.html')


@app.route('/about')
def about():
    """Hakkında sayfası."""
    return render_template('about.html')


@app.route('/education')
def education():
    """Eğitim sayfası."""
    return render_template('education.html')


@app.route('/calculator')
def calculator_page():
    """Hesaplama sayfası."""
    return render_template('calculator.html')


@app.route('/optimizer')
def optimizer_page():
    """Optimizasyon sayfası."""
    return render_template('optimizer.html')


@app.route('/primer-designer')
def primer_designer_page():
    """Primer tasarım sayfası."""
    return render_template('primer_designer.html')


@app.route('/test')
def test_page():
    """Test sayfası."""
    return render_template('test.html')


@app.route('/static/<path:path>')
def send_static(path):
    """Statik dosyaları serve et."""
    return send_from_directory('static', path)


@app.route('/calculate/tm', methods=['POST'])
def calculate_tm():
    """Erime sıcaklığı (Tm) hesapla."""
    try:
        data = request.get_json()
        
        primer_sequence = data.get('primer_sequence', '')
        
        if not primer_sequence:
            return jsonify({'error': 'Primer dizisi gerekli'}), 400
            
        tm = calculator.calculate_tm(primer_sequence)
        
        return jsonify({
            'tm': tm,
            'primer_sequence': primer_sequence
        })
    except Exception as e:
        logger.error(f"Tm hesaplanırken hata: {str(e)}")
        return jsonify({'error': f'Tm hesaplanırken bir hata oluştu: {str(e)}'}), 500


@app.route('/calculate/gc', methods=['POST'])
def calculate_gc():
    """GC içeriği hesapla."""
    try:
        data = request.get_json()
        
        sequence = data.get('sequence', '')
        
        if not sequence:
            return jsonify({'error': 'DNA dizisi gerekli'}), 400
            
        gc_content = calculator.calculate_gc_content(sequence)
        
        return jsonify({
            'gc_content': gc_content,
            'sequence': sequence
        })
    except Exception as e:
        logger.error(f"GC içeriği hesaplanırken hata: {str(e)}")
        return jsonify({'error': f'GC içeriği hesaplanırken bir hata oluştu: {str(e)}'}), 500


@app.route('/calculate/extension-time', methods=['POST'])
def calculate_extension_time():
    """Uzama süresi hesapla."""
    try:
        data = request.get_json()
        
        template_length = data.get('template_length', 0)
        
        try:
            template_length = int(template_length)
        except ValueError:
            return jsonify({'error': 'Şablon uzunluğu bir sayı olmalı'}), 400
            
        if template_length <= 0:
            return jsonify({'error': 'Şablon uzunluğu pozitif bir sayı olmalı'}), 400
            
        extension_time = calculator.calculate_extension_time(template_length)
        
        return jsonify({
            'extension_time': extension_time,
            'template_length': template_length
        })
    except Exception as e:
        logger.error(f"Uzama süresi hesaplanırken hata: {str(e)}")
        return jsonify({'error': f'Uzama süresi hesaplanırken bir hata oluştu: {str(e)}'}), 500


@app.route('/calculate/annealing-temp', methods=['POST'])
def calculate_annealing_temp():
    """Bağlanma sıcaklığı hesapla."""
    try:
        data = request.get_json()
        
        forward_primer = data.get('forward_primer', '')
        reverse_primer = data.get('reverse_primer', '')
        
        if not forward_primer or not reverse_primer:
            return jsonify({'error': 'İleri ve geri primer dizileri gerekli'}), 400
            
        annealing_temp = calculator.calculate_annealing_temp(forward_primer, reverse_primer)
        
        forward_tm = calculator.calculate_tm(forward_primer)
        reverse_tm = calculator.calculate_tm(reverse_primer)
        
        return jsonify({
            'annealing_temp': annealing_temp,
            'forward_tm': forward_tm,
            'reverse_tm': reverse_tm,
            'forward_primer': forward_primer,
            'reverse_primer': reverse_primer
        })
    except Exception as e:
        logger.error(f"Bağlanma sıcaklığı hesaplanırken hata: {str(e)}")
        return jsonify({'error': f'Bağlanma sıcaklığı hesaplanırken bir hata oluştu: {str(e)}'}), 500


@app.route('/calculate/cycle-number', methods=['POST'])
def calculate_cycle_number():
    """PCR döngü sayısı hesapla."""
    try:
        data = request.get_json()
        
        template_concentration = data.get('template_concentration', 0)
        target_yield = data.get('target_yield', 0)
        
        try:
            template_concentration = float(template_concentration)
            target_yield = float(target_yield)
        except ValueError:
            return jsonify({'error': 'Konsantrasyon değerleri sayı olmalı'}), 400
            
        if template_concentration <= 0 or target_yield <= 0:
            return jsonify({'error': 'Konsantrasyon değerleri pozitif sayılar olmalı'}), 400
            
        cycle_number = calculator.calculate_cycle_number(template_concentration, target_yield)
        
        return jsonify({
            'cycle_number': cycle_number,
            'template_concentration': template_concentration,
            'target_yield': target_yield
        })
    except Exception as e:
        logger.error(f"Döngü sayısı hesaplanırken hata: {str(e)}")
        return jsonify({'error': f'Döngü sayısı hesaplanırken bir hata oluştu: {str(e)}'}), 500


@app.route('/optimize', methods=['POST'])
def optimize_pcr():
    """PCR parametrelerini optimize et."""
    try:
        data = request.get_json()
        
        # İsteğe bağlı parametreler
        template_length = data.get('template_length')
        gc_content = data.get('gc_content')
        forward_primer = data.get('forward_primer', '')
        reverse_primer = data.get('reverse_primer', '')
        template_concentration = data.get('template_concentration')
        target_yield = data.get('target_yield')
        sequence = data.get('sequence', '')
        is_diagnostic = data.get('is_diagnostic', False)
        
        # Sayısal değerleri dönüştür
        try:
            if template_length is not None:
                template_length = int(template_length)
            if gc_content is not None:
                gc_content = float(gc_content)
            if template_concentration is not None:
                template_concentration = float(template_concentration)
            if target_yield is not None:
                target_yield = float(target_yield)
        except ValueError:
            return jsonify({'error': 'Sayısal değerler geçerli sayılar olmalı'}), 400
        
        # GC içeriğini hesapla (eğer dizi sağlanmışsa)
        if sequence and not gc_content:
            gc_content = calculator.calculate_gc_content(sequence)
        
        # Tam protokol oluştur
        protocol = optimizer.create_complete_protocol(
            template_length=template_length,
            forward_primer=forward_primer,
            reverse_primer=reverse_primer,
            template_concentration=template_concentration,
            target_yield=target_yield,
            gc_content=gc_content,
            sequence=sequence,
            is_diagnostic=is_diagnostic
        )
        
        # Protokol üreticisi ile formatlanmış protokol oluştur
        formatted_protocol = protocol_generator.generate_protocol(protocol)
        
        response = {
            'protocol': protocol,
            'formatted_protocol': formatted_protocol,
            'input_parameters': {
                'template_length': template_length,
                'gc_content': gc_content,
                'forward_primer': forward_primer,
                'reverse_primer': reverse_primer,
                'template_concentration': template_concentration,
                'target_yield': target_yield,
                'sequence': sequence,
                'is_diagnostic': is_diagnostic
            }
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"PCR optimizasyonu sırasında hata: {str(e)}")
        return jsonify({'error': f'PCR optimizasyonu sırasında bir hata oluştu: {str(e)}'}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    """Dosya yükle."""
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya bulunamadı'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400
        
    if file and allowed_file(file.filename):
        # Güvenli bir dosya adı oluştur
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        saved_filename = f"{timestamp}_{filename}"
        
        # Dosyayı kaydet
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(file_path)
        
        try:
            # Dosyayı oku
            with open(file_path, 'r') as f:
                content = f.read()
            
            # FASTA formatını kontrol et ve işle
            if file.filename.endswith(('.fasta', '.fa')):
                sequence = parse_fasta(content)
            else:
                sequence = ''.join(char for char in content if char.upper() in 'ATGC')
            
            if not sequence:
                os.remove(file_path)  # Gereksiz dosyayı sil
                return jsonify({'error': 'Geçerli bir DNA dizisi bulunamadı'}), 400
            
            # GC içeriğini hesapla
            gc_content = calculator.calculate_gc_content(sequence)
            
            # İşlem tamamlandığında dosyayı sil (opsiyonel)
            os.remove(file_path)
            
            return jsonify({
                'sequence': sequence,
                'gc_content': gc_content,
                'length': len(sequence)
            })
        except Exception as e:
            logger.error(f"Dosya işlenirken hata: {str(e)}")
            # Hata durumunda dosyayı temizle
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': f'Dosya işlenirken bir hata oluştu: {str(e)}'}), 500
    
    return jsonify({'error': 'İzin verilmeyen dosya türü'}), 400


# Primer tasarım ve analiz endpoint'leri
@app.route('/primer/analyze', methods=['POST'])
def analyze_primer():
    """Primer(ler)i analiz et."""
    try:
        data = request.get_json()
        
        forward_primer = data.get('forward_primer', '')
        reverse_primer = data.get('reverse_primer', '')
        
        if not forward_primer and not reverse_primer:
            return jsonify({'error': 'En az bir primer dizisi gerekli'}), 400
        
        # Her iki primer de varsa, çift olarak analiz et
        if forward_primer and reverse_primer:
            result = primer_designer.evaluate_primer_pair(forward_primer, reverse_primer)
            return jsonify(result)
        # Sadece bir primer varsa, tekli analiz yap
        elif forward_primer:
            result = primer_designer.evaluate_primer(forward_primer)
            return jsonify({'primer': result})
        else:
            result = primer_designer.evaluate_primer(reverse_primer)
            return jsonify({'primer': result})
            
    except Exception as e:
        logger.error(f"Primer analizi sırasında hata: {str(e)}")
        return jsonify({'error': f'Primer analizi sırasında bir hata oluştu: {str(e)}'}), 500


@app.route('/primer/design', methods=['POST'])
def design_primer():
    """DNA dizisi için primer tasarla."""
    try:
        data = request.get_json()
        
        template_sequence = data.get('template_sequence', '')
        target_length = data.get('target_length')
        
        if not template_sequence:
            return jsonify({'error': 'DNA dizisi gerekli'}), 400
            
        # Sayıya dönüştür
        if target_length is not None:
            try:
                target_length = int(target_length)
            except ValueError:
                return jsonify({'error': 'Hedef uzunluk bir sayı olmalı'}), 400
        
        # Primer tasarla
        result = primer_designer.suggest_primers(template_sequence, target_length)
        
        return jsonify(result)
            
    except Exception as e:
        logger.error(f"Primer tasarımı sırasında hata: {str(e)}")
        return jsonify({'error': f'Primer tasarımı sırasında bir hata oluştu: {str(e)}'}), 500


def parse_fasta(content):
    """FASTA formatını ayrıştır ve DNA dizisini döndür."""
    lines = content.strip().split('\n')
    sequence = ''
    
    for line in lines:
        if not line.startswith('>'):
            sequence += line.strip()
    
    # Sadece geçerli DNA karakterlerini tut
    return ''.join(char for char in sequence if char.upper() in 'ATGC')


@app.errorhandler(404)
def page_not_found(e):
    """404 hatası sayfası."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """500 hatası sayfası."""
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True) 