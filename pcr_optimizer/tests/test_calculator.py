"""
PCRCalculator sınıfı için birim testleri.
"""

import pytest
import sys
import os

# src dizinini Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.calculator import PCRCalculator


class TestPCRCalculator:
    """PCRCalculator sınıfı için test sınıfı."""
    
    def setup_method(self):
        """Her test için çalışacak kurulum metodu."""
        self.calculator = PCRCalculator()
    
    def test_calculate_tm(self):
        """calculate_tm metodunu test eder."""
        # Kısa primer için Tm hesaplama
        assert self.calculator.calculate_tm("ATGCTAGC") > 0
        
        # Uzun primer için Tm hesaplama
        assert self.calculator.calculate_tm("ATGCTAGCTAGCTAGCTAGCTAGC") > 0
        
        # Boş dizi için Tm hesaplama
        assert self.calculator.calculate_tm("") == 0
        
        # GC bakımından zengin ve fakir primerler için karşılaştırma
        gc_rich = "GCGCGCGCGC"  # %100 GC
        at_rich = "ATATATATAT"  # %0 GC
        assert self.calculator.calculate_tm(gc_rich) > self.calculator.calculate_tm(at_rich)
    
    def test_calculate_gc_content(self):
        """calculate_gc_content metodunu test eder."""
        # 50% GC içeriği
        assert self.calculator.calculate_gc_content("ATGC") == 50.0
        
        # 100% GC içeriği
        assert self.calculator.calculate_gc_content("GCGCGC") == 100.0
        
        # 0% GC içeriği
        assert self.calculator.calculate_gc_content("ATATAT") == 0.0
        
        # Boş dizi için GC içeriği
        assert self.calculator.calculate_gc_content("") == 0.0
        
        # Karışık dizi için GC içeriği
        assert 25.0 <= self.calculator.calculate_gc_content("ATGCATATATATA") <= 25.1
    
    def test_calculate_extension_time(self):
        """calculate_extension_time metodunu test eder."""
        # Kısa DNA için uzama süresi (30 saniye minimum)
        assert self.calculator.calculate_extension_time(100) == 30
        
        # Uzun DNA için uzama süresi
        long_dna_length = 5000
        expected_min_time = long_dna_length / self.calculator.polymerase_speed * 1.2
        assert self.calculator.calculate_extension_time(long_dna_length) >= expected_min_time
        
        # DNA uzunluğu arttıkça uzama süresi de artmalı
        assert (self.calculator.calculate_extension_time(2000) < 
                self.calculator.calculate_extension_time(4000))
    
    def test_calculate_annealing_temp(self):
        """calculate_annealing_temp metodunu test eder."""
        # İki primer için bağlanma sıcaklığı hesaplama
        forward = "ATGCTAGCTAGCTAGC"
        reverse = "TAGCTAGCTAGCTAGC"
        annealing_temp = self.calculator.calculate_annealing_temp(forward, reverse)
        
        # Bağlanma sıcaklığı genellikle en düşük Tm'den 5°C daha düşüktür
        forward_tm = self.calculator.calculate_tm(forward)
        reverse_tm = self.calculator.calculate_tm(reverse)
        expected_temp = min(forward_tm, reverse_tm) - 5
        
        assert annealing_temp == expected_temp
    
    def test_calculate_cycle_number(self):
        """calculate_cycle_number metodunu test eder."""
        # Geçersiz değerler için varsayılan döngü sayısı kontrolü
        assert self.calculator.calculate_cycle_number(0, 10) == 30
        assert self.calculator.calculate_cycle_number(10, 0) == 30
        
        # Geçerli değerler için döngü sayısı hesaplama
        assert 15 <= self.calculator.calculate_cycle_number(1, 1000) <= 40
        
        # Düşük başlangıç konsantrasyonu ve yüksek hedef verim için daha fazla döngü
        low_conc_cycles = self.calculator.calculate_cycle_number(0.1, 100)
        high_conc_cycles = self.calculator.calculate_cycle_number(10, 100)
        assert low_conc_cycles > high_conc_cycles 