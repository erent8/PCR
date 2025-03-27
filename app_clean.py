"""
PCR Optimizer ana web uygulaması.
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import io
from datetime import datetime

# Core sınıflarımızı içe aktar
from core.calculator import PCRCalculator
from core.optimizer import PCROptimizer
from core.protocol_generator import ProtocolGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pcr-optimizer-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ana dizini oluştur (eğer yoksa)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Ana sınıfları başlat
calculator = PCRCalculator()
optimizer = PCROptimizer()
protocol_generator = ProtocolGenerator(optimizer)


@app.route('/')
def index():
    """Ana sayfa."""
    return render_template('index.html', now=datetime.now())


@app.route('/calculator', methods=['GET', 'POST'])
def calculator_page():
    """Hesaplama sayfası."""
    results = None
    
    if request.method == 'POST':
        # Formdan gelen verileri al
        forward_primer = request.form.get('forward_primer', '')
        reverse_primer = request.form.get('reverse_primer', '')
        template_length = request.form.get('template_length', 0)
        sequence = request.form.get('sequence', '')
        
        # Doğrulama
        if not forward_primer and not reverse_primer and not sequence:
            return render_template('calculator.html', error="En az bir primer dizisi veya DNA dizisi gerekli.", now=datetime.now())
        
        try:
            template_length = int(template_length) if template_length else 0
        except ValueError:
            return render_template('calculator.html', error="Şablon uzunluğu bir sayı olmalıdır.", now=datetime.now())
        
        # Hesaplamaları yap
        results = {}
        
        if forward_primer:
            results['forward_tm'] = calculator.calculate_tm(forward_primer)
            results['forward_gc'] = calculator.calculate_gc_content(forward_primer)
        
        if reverse_primer:
            results['reverse_tm'] = calculator.calculate_tm(reverse_primer)
            results['reverse_gc'] = calculator.calculate_gc_content(reverse_primer)
        
        if forward_primer and reverse_primer:
            results['annealing_temp'] = calculator.calculate_annealing_temp(
                forward_primer, reverse_primer
            )
        
        if sequence:
            results['sequence_gc'] = calculator.calculate_gc_content(sequence)
        
        if template_length > 0:
            results['extension_time'] = calculator.calculate_extension_time(template_length)
            
    return render_template('calculator.html', results=results, now=datetime.now())


@app.route('/optimizer', methods=['GET', 'POST'])
def optimizer_page():
    """Optimizasyon sayfası."""
    if request.method == 'POST':
        # Formdan verileri al
        try:
            # Primer dizileri
            forward_primer = request.form.get('forward_primer', '')
            reverse_primer = request.form.get('reverse_primer', '')
            
            # Şablon özellikleri
            template_length = int(request.form.get('template_length', 0) or 0)
            template_gc = float(request.form.get('template_gc', 0) or 0)
            
            # Konsantrasyon bilgileri
            template_concentration = float(request.form.get('template_concentration', 0) or 0)
            target_yield = float(request.form.get('target_yield', 0) or 0)
            
            # Ek bilgiler
            is_diagnostic = 'is_diagnostic' in request.form
            
            # Verileri doğrula
            if template_length <= 0:
                return render_template('optimizer.html', error="Geçerli bir şablon uzunluğu giriniz.", now=datetime.now())
                
            # Protokolü oluştur
            protocol = optimizer.create_complete_protocol(
                template_length=template_length,
                forward_primer=forward_primer,
                reverse_primer=reverse_primer,
                gc_content=template_gc if template_gc > 0 else None,
                template_concentration=template_concentration if template_concentration > 0 else None,
                target_yield=target_yield if target_yield > 0 else None,
                is_diagnostic=is_diagnostic
            )
            
            # Parametreleri kaydet
            params = {
                "forward_primer": forward_primer,
                "reverse_primer": reverse_primer,
                "template_length": template_length,
                "template_gc": template_gc,
                "template_concentration": template_concentration,
                "target_yield": target_yield,
                "is_diagnostic": is_diagnostic
            }
            
            # Raporu oluştur
            report_text = protocol_generator.generate_report(protocol, params)
            
            return render_template('optimizer.html', protocol=protocol, report=report_text, now=datetime.now())
            
        except Exception as e:
            return render_template('optimizer.html', error=f"Hata: {str(e)}", now=datetime.now())
    
    return render_template('optimizer.html', now=datetime.now())


@app.route('/download_protocol', methods=['POST'])
def download_protocol():
    """Protokolü dosya olarak indir."""
    try:
        protocol_data = request.json.get('protocol')
        format_type = request.json.get('format', 'text')
        
        if not protocol_data:
            return jsonify({"error": "Protokol verisi bulunamadı."}), 400
            
        # Formatını belirle
        if format_type == 'json':
            content = protocol_generator.protocol_to_json(protocol_data)
            mimetype = 'application/json'
            ext = 'json'
        elif format_type == 'csv':
            content = protocol_generator.protocol_to_csv(protocol_data)
            mimetype = 'text/csv'
            ext = 'csv'
        else:  # text
            content = protocol_generator.protocol_to_text(protocol_data)
            mimetype = 'text/plain'
            ext = 'txt'
            
        # Dosya adını oluştur
        filename = f"pcr_protocol_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        
        # Dosyayı oluştur ve gönder
        buffer = io.BytesIO(content.encode('utf-8'))
        buffer.seek(0)
        
        return send_file(
            buffer, 
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/about')
def about():
    """Hakkında sayfası."""
    return render_template('about.html', now=datetime.now())


@app.errorhandler(404)
def page_not_found(e):
    """404 hata sayfası."""
    return render_template('404.html', now=datetime.now()), 404


@app.errorhandler(500)
def server_error(e):
    """500 hata sayfası."""
    return render_template('500.html', now=datetime.now()), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 