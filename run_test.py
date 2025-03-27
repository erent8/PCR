#!/usr/bin/env python
"""
PCR Optimizer test scripti.
Test verilerini kullanarak PCR optimizasyonunu gerçekleştirir ve sonuçları yazdırır.
"""

import sys
import os
from datetime import datetime

# Gerekli modülleri içe aktar
try:
    from src.core.calculator import PCRCalculator
    from src.core.optimizer import PCROptimizer
    from src.core.protocol_generator import ProtocolGenerator
    from test_data import (
        SHORT_PCR, LONG_PCR, GC_RICH_PCR, AT_RICH_PCR, 
        DIAGNOSTIC_PCR, COLONY_PCR, MINIMAL_TEST_DATA
    )
except ImportError:
    # Çalışma dizininden göreceli olarak içe aktar
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from src.core.calculator import PCRCalculator
    from src.core.optimizer import PCROptimizer
    from src.core.protocol_generator import ProtocolGenerator
    from test_data import (
        SHORT_PCR, LONG_PCR, GC_RICH_PCR, AT_RICH_PCR, 
        DIAGNOSTIC_PCR, COLONY_PCR, MINIMAL_TEST_DATA
    )

def print_separator(title):
    """Ayırıcı çizgi ve başlık yazdırır."""
    print("\n" + "="*50)
    print(f" {title} ".center(50, "-"))
    print("="*50)

def print_protocol(name, protocol, protocol_generator):
    """Protokolü metin formatında yazdırır."""
    print_separator(name)
    print(protocol_generator.protocol_to_text(protocol))
    print("-"*50)

def run_tests():
    """Tüm test verilerini kullanarak PCR optimizasyonlarını gerçekleştirir."""
    # Ana sınıfları başlat
    calculator = PCRCalculator()
    optimizer = PCROptimizer()
    protocol_generator = ProtocolGenerator(optimizer)
    
    print("\nPCR OPTİMİZASYON TEST ÇALIŞMASI")
    print(f"Tarih: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Test verilerini ve isimlerini bir liste içinde tut
    test_cases = [
        ("Kısa PCR Protokolü", SHORT_PCR),
        ("Uzun PCR Protokolü", LONG_PCR),
        ("GC-Zengin PCR Protokolü", GC_RICH_PCR),
        ("AT-Zengin PCR Protokolü", AT_RICH_PCR),
        ("Tanısal PCR Protokolü", DIAGNOSTIC_PCR),
        ("Koloni PCR Protokolü", COLONY_PCR),
        ("Minimal Test Verisi", MINIMAL_TEST_DATA)
    ]
    
    # Her bir test durumu için protokol oluştur ve yazdır
    for name, test_data in test_cases:
        # Test verilerini protokol oluşturmak için kullan
        protocol = optimizer.create_complete_protocol(
            template_length=test_data.get("template_length"),
            forward_primer=test_data.get("forward_primer"),
            reverse_primer=test_data.get("reverse_primer"),
            gc_content=test_data.get("template_gc"),
            template_concentration=test_data.get("template_concentration"),
            target_yield=test_data.get("target_yield"),
            is_diagnostic=test_data.get("is_diagnostic", False)
        )
        
        # Protokolü yazdır
        print_protocol(name, protocol, protocol_generator)
        
        # Primer hesaplamaları yazdır (eğer mevcutsa)
        if "forward_primer" in test_data and "reverse_primer" in test_data:
            forward = test_data["forward_primer"]
            reverse = test_data["reverse_primer"]
            
            print(f"Forward Primer: {forward}")
            print(f"  - Tm: {calculator.calculate_tm(forward):.1f}°C")
            print(f"  - GC: %{calculator.calculate_gc_content(forward):.1f}")
            
            print(f"Reverse Primer: {reverse}")
            print(f"  - Tm: {calculator.calculate_tm(reverse):.1f}°C")
            print(f"  - GC: %{calculator.calculate_gc_content(reverse):.1f}")
            
            print(f"Önerilen Bağlanma Sıcaklığı: {calculator.calculate_annealing_temp(forward, reverse):.1f}°C")
        
        print("\n")

if __name__ == "__main__":
    try:
        run_tests()
        print("Test çalışması başarıyla tamamlandı.")
    except Exception as e:
        print(f"Hata: {str(e)}")
        sys.exit(1) 