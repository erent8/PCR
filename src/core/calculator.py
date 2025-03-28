"""
PCR reaksiyonu için temel hesaplamaları yapan modül.
"""

import math
import numpy as np


class PCRCalculator:
    """PCR parametrelerini hesaplamak için ana sınıf."""
    
    def __init__(self):
        """PCRCalculator sınıfı için başlatıcı."""
        # Polimeraz enziminin aktivite hızı (nükleotid/saniye)
        self.polymerase_speed = 1000  # Taq polimeraz için yaklaşık değer
    
    def calculate_tm(self, primer_sequence):
        """
        Primer erime sıcaklığını (Tm) hesaplar.
        
        Basit hesaplama: 4 * (G+C) + 2 * (A+T)
        Daha doğru hesaplama için Biopython kullanımı önerilir.
        
        Args:
            primer_sequence (str): Primer dizisi
            
        Returns:
            float: Tahmini erime sıcaklığı (°C)
        """
        if not primer_sequence:
            return 0
            
        sequence = primer_sequence.upper()
        g_count = sequence.count('G')
        c_count = sequence.count('C')
        a_count = sequence.count('A')
        t_count = sequence.count('T')
        
        # Basit Tm hesaplama formülü
        if len(sequence) < 14:
            tm = 2 * (a_count + t_count) + 4 * (g_count + c_count)
        else:
            # Uzun primerler için
            tm = 64.9 + 41 * (g_count + c_count - 16.4) / len(sequence)
            
        return round(tm, 1)
    
    def calculate_gc_content(self, sequence):
        """
        DNA dizisinin GC içeriğini yüzde olarak hesaplar.
        
        Args:
            sequence (str): DNA dizisi
            
        Returns:
            float: GC içeriği yüzdesi
        """
        if not sequence:
            return 0
            
        sequence = sequence.upper()
        gc_count = sequence.count('G') + sequence.count('C')
        total_length = len(sequence)
        
        gc_percentage = (gc_count / total_length) * 100
        return round(gc_percentage, 1)
    
    def calculate_extension_time(self, template_length):
        """
        DNA uzunluğuna göre uzama süresini hesaplar.
        
        Args:
            template_length (int): Hedef DNA'nın baz çifti uzunluğu
            
        Returns:
            int: Önerilen uzama süresi (saniye)
        """
        # Polimeraz hızına göre hesaplama
        extension_time = template_length / self.polymerase_speed
        
        # En az 30 saniye veya daha fazla
        extension_time = max(30, extension_time)
        
        # Güvenlik payı için %20 artırma
        extension_time *= 1.2
        
        return math.ceil(extension_time)
    
    def calculate_annealing_temp(self, forward_primer, reverse_primer):
        """
        Bağlanma sıcaklığını hesaplar.
        
        Args:
            forward_primer (str): İleri primer dizisi
            reverse_primer (str): Geri primer dizisi
            
        Returns:
            float: Önerilen bağlanma sıcaklığı (°C)
        """
        forward_tm = self.calculate_tm(forward_primer)
        reverse_tm = self.calculate_tm(reverse_primer)
        
        # Önerilen bağlanma sıcaklığı genellikle en düşük Tm'den 5°C daha düşüktür
        annealing_temp = min(forward_tm, reverse_tm) - 5
        
        return round(annealing_temp, 1)
    
    def calculate_cycle_number(self, template_concentration, target_yield):
        """
        PCR döngü sayısını hesaplar.
        
        Args:
            template_concentration (float): Şablon DNA konsantrasyonu (ng/μL)
            target_yield (float): Hedeflenen ürün miktarı (ng/μL)
            
        Returns:
            int: Önerilen döngü sayısı
        """
        if template_concentration <= 0 or target_yield <= 0:
            return 30  # Varsayılan döngü sayısı
            
        # Her döngüde teorik olarak 2 kat artış
        cycles = math.log2(target_yield / template_concentration)
        
        # Pratik sınırlar içinde tutma
        cycles = max(15, min(40, math.ceil(cycles)))
        
        return cycles 