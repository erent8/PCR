"""
PCR koşullarını optimize eden modül.
"""

from .calculator import PCRCalculator


class PCROptimizer:
    """PCR koşullarını optimize etmek için ana sınıf."""
    
    def __init__(self):
        """PCROptimizer sınıfı için başlatıcı."""
        self.calculator = PCRCalculator()
        
        # Standart PCR sıcaklık değerleri
        self.default_denaturation_temp = 95  # °C
        self.default_denaturation_time = 30  # saniye
        self.default_annealing_time = 30  # saniye
        self.default_extension_temp = 72  # °C
        self.default_final_extension_time = 300  # saniye (5 dakika)
        self.default_initial_denaturation_time = 180  # saniye (3 dakika)
        
    def optimize_temperatures(self, forward_primer=None, reverse_primer=None, gc_content=None):
        """
        PCR sıcaklık parametrelerini optimize eder.
        
        Args:
            forward_primer (str, optional): İleri primer dizisi
            reverse_primer (str, optional): Geri primer dizisi
            gc_content (float, optional): Hedef dizinin GC içeriği yüzdesi
            
        Returns:
            dict: Optimize edilmiş sıcaklık değerleri
        """
        # Varsayılan değerlerle başla
        optimized_temps = {
            "denaturation_temp": self.default_denaturation_temp,
            "annealing_temp": 55,  # Varsayılan bağlanma sıcaklığı
            "extension_temp": self.default_extension_temp
        }
        
        # Primer dizileri verilmişse, bağlanma sıcaklığını hesapla
        if forward_primer and reverse_primer:
            optimized_temps["annealing_temp"] = self.calculator.calculate_annealing_temp(
                forward_primer, reverse_primer
            )
        
        # GC içeriği verilmişse, denatürasyon sıcaklığını ayarla
        if gc_content:
            # GC içeriği yüksekse, denatürasyon sıcaklığını artır
            if gc_content > 65:
                optimized_temps["denaturation_temp"] = 98
            elif gc_content > 55:
                optimized_temps["denaturation_temp"] = 97
        
        return optimized_temps
    
    def optimize_times(self, template_length=None, gc_content=None):
        """
        PCR süre parametrelerini optimize eder.
        
        Args:
            template_length (int, optional): Hedef DNA'nın baz çifti uzunluğu
            gc_content (float, optional): Hedef dizinin GC içeriği yüzdesi
            
        Returns:
            dict: Optimize edilmiş süre değerleri
        """
        # Varsayılan değerlerle başla
        optimized_times = {
            "initial_denaturation_time": self.default_initial_denaturation_time,
            "denaturation_time": self.default_denaturation_time,
            "annealing_time": self.default_annealing_time,
            "extension_time": 60,  # Varsayılan uzama süresi (1 dakika)
            "final_extension_time": self.default_final_extension_time
        }
        
        # Şablon uzunluğu verilmişse, uzama süresini hesapla
        if template_length:
            optimized_times["extension_time"] = self.calculator.calculate_extension_time(template_length)
            
            # Uzun şablonlar için son uzama süresini uzat
            if template_length > 3000:
                optimized_times["final_extension_time"] = 600  # 10 dakika
        
        # GC içeriği verilmişse, denatürasyon süresini ayarla
        if gc_content:
            # GC içeriği yüksekse, denatürasyon süresini uzat
            if gc_content > 65:
                optimized_times["initial_denaturation_time"] = 300  # 5 dakika
                optimized_times["denaturation_time"] = 45  # 45 saniye
        
        return optimized_times
    
    def optimize_cycle_number(self, template_concentration=None, target_yield=None, is_diagnostic=False):
        """
        PCR döngü sayısını optimize eder.
        
        Args:
            template_concentration (float, optional): Şablon DNA konsantrasyonu (ng/μL)
            target_yield (float, optional): Hedeflenen ürün miktarı (ng/μL)
            is_diagnostic (bool): Tanısal PCR ise True, klonlama için ise False
            
        Returns:
            int: Optimize edilmiş döngü sayısı
        """
        # Varsayılan döngü sayısı
        default_cycles = 25 if not is_diagnostic else 40
        
        # Şablon konsantrasyonu ve hedef verim verilmişse, döngü sayısını hesapla
        if template_concentration and target_yield:
            return self.calculator.calculate_cycle_number(template_concentration, target_yield)
        
        return default_cycles
    
    def create_complete_protocol(self, template_length=None, forward_primer=None, 
                                reverse_primer=None, template_concentration=None, 
                                target_yield=None, sequence=None, is_diagnostic=False, gc_content=None):
        """
        Tam bir PCR protokolü oluşturur.
        
        Args:
            template_length (int, optional): Hedef DNA'nın baz çifti uzunluğu
            forward_primer (str, optional): İleri primer dizisi
            reverse_primer (str, optional): Geri primer dizisi
            template_concentration (float, optional): Şablon DNA konsantrasyonu (ng/μL)
            target_yield (float, optional): Hedeflenen ürün miktarı (ng/μL)
            sequence (str, optional): Hedef DNA dizisi
            is_diagnostic (bool): Tanısal PCR ise True, klonlama için ise False
            gc_content (float, optional): Hedef dizinin GC içeriği yüzdesi
            
        Returns:
            dict: Tam PCR protokolü
        """
        # GC içeriğini hesapla (eğer dizi verilmişse ve gc_content parametresi verilmemişse)
        if not gc_content and sequence:
            gc_content = self.calculator.calculate_gc_content(sequence)
        
        # Sıcaklık ve süre optimizasyonlarını yap
        optimized_temps = self.optimize_temperatures(forward_primer, reverse_primer, gc_content)
        optimized_times = self.optimize_times(template_length, gc_content)
        cycle_number = self.optimize_cycle_number(template_concentration, target_yield, is_diagnostic)
        
        # Tam protokolü oluştur
        protocol = {
            "initial_denaturation": {
                "temperature": optimized_temps["denaturation_temp"],
                "time": optimized_times["initial_denaturation_time"]
            },
            "cycles": {
                "count": cycle_number,
                "denaturation": {
                    "temperature": optimized_temps["denaturation_temp"],
                    "time": optimized_times["denaturation_time"]
                },
                "annealing": {
                    "temperature": optimized_temps["annealing_temp"],
                    "time": optimized_times["annealing_time"]
                },
                "extension": {
                    "temperature": optimized_temps["extension_temp"],
                    "time": optimized_times["extension_time"]
                }
            },
            "final_extension": {
                "temperature": optimized_temps["extension_temp"],
                "time": optimized_times["final_extension_time"]
            },
            "hold": {
                "temperature": 4,
                "time": "indefinite"
            }
        }
        
        # Ekstra bilgileri ekle
        if gc_content:
            protocol["gc_content"] = gc_content
            
        # Giriş parametrelerini protokole ekle
        protocol["template_length"] = template_length
        if forward_primer and reverse_primer:
            protocol["primers"] = {
                "forward": forward_primer,
                "reverse": reverse_primer
            }
        if template_concentration:
            protocol["template_concentration"] = template_concentration
        if target_yield:
            protocol["target_yield"] = target_yield
        protocol["is_diagnostic"] = is_diagnostic
            
        return protocol 