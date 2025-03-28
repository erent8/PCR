"""
PCR primerleri tasarlamak ve analiz etmek için modül.
"""

import re
from collections import Counter


class PrimerDesigner:
    """PCR primerleri tasarlamak ve değerlendirmek için ana sınıf."""
    
    def __init__(self):
        """PrimerDesigner sınıfı için başlatıcı."""
        # İdeal primer uzunlukları
        self.min_length = 18
        self.max_length = 30
        # İdeal GC içeriği aralığı
        self.min_gc = 40
        self.max_gc = 60
        # İdeal Tm aralığı (°C)
        self.min_tm = 50
        self.max_tm = 65
        # Primer 3' ucunda G veya C olması tercih edilir (GC clamp)
        self.gc_clamp = True
        
    def calculate_tm(self, primer_sequence):
        """
        Primer erime sıcaklığını (Tm) hesaplar.
        
        Basit hesaplama: 4 * (G+C) + 2 * (A+T)
        Daha uzun primerler için daha kesin formül kullanılır.
        
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
            # Uzun primerler için daha kesin formül
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
    
    def check_secondary_structure(self, primer):
        """
        Primer'in kendi içinde ikincil yapılar (hairpin) oluşturma potansiyelini kontrol eder.
        
        Basit bir yaklaşım kullanarak, kendi içinde eşleşme olasılığını değerlendirir.
        
        Args:
            primer (str): Primer dizisi
            
        Returns:
            tuple: (hairpin_olasılığı, açıklama)
        """
        primer = primer.upper()
        
        # En az 3 baz eşleşmesi gerekir
        min_hairpin_length = 3
        
        # Tersine çevrilmiş primer dizisini oluştur
        reverse_comp = self.reverse_complement(primer)
        
        # Kendi içinde eşleşme kontrolü
        max_match = 0
        for i in range(len(primer) - min_hairpin_length + 1):
            for j in range(len(reverse_comp) - min_hairpin_length + 1):
                match_length = 0
                while (i + match_length < len(primer) and 
                       j + match_length < len(reverse_comp) and 
                       primer[i + match_length] == reverse_comp[j + match_length]):
                    match_length += 1
                
                if match_length >= min_hairpin_length:
                    max_match = max(max_match, match_length)
        
        # Hairpin değerlendirmesi
        if max_match == 0:
            return (0, "İkincil yapı riski yok")
        elif max_match < 5:
            return (max_match/10, f"Düşük ikincil yapı riski (Eşleşme: {max_match} baz)")
        elif max_match < 7:
            return (max_match/10, f"Orta ikincil yapı riski (Eşleşme: {max_match} baz)")
        else:
            return (max_match/10, f"Yüksek ikincil yapı riski (Eşleşme: {max_match} baz)")
    
    def check_primer_dimer(self, primer1, primer2=None):
        """
        İki primer arasında dimer oluşma potansiyelini kontrol eder.
        Tek primer verilirse, kendisi ile dimer oluşumunu kontrol eder.
        
        Args:
            primer1 (str): Birinci primer dizisi
            primer2 (str, optional): İkinci primer dizisi
            
        Returns:
            tuple: (dimer_olasılığı, açıklama)
        """
        primer1 = primer1.upper()
        
        if primer2 is None:
            primer2 = primer1
        else:
            primer2 = primer2.upper()
        
        # En az 3 baz eşleşmesi gerekir
        min_dimer_length = 3
        
        # İkinci primer dizisinin tamamlayıcısını oluştur
        primer2_comp = self.complement(primer2)
        
        # Primerler arası eşleşme kontrolü
        max_match = 0
        for i in range(len(primer1) - min_dimer_length + 1):
            for j in range(len(primer2_comp) - min_dimer_length + 1):
                match_length = 0
                while (i + match_length < len(primer1) and 
                       j + match_length < len(primer2_comp) and 
                       primer1[i + match_length] == primer2_comp[j + match_length]):
                    match_length += 1
                
                if match_length >= min_dimer_length:
                    max_match = max(max_match, match_length)
        
        # Dimer değerlendirmesi
        if max_match == 0:
            return (0, "Dimer oluşma riski yok")
        elif max_match < 5:
            return (max_match/10, f"Düşük dimer oluşma riski (Eşleşme: {max_match} baz)")
        elif max_match < 7:
            return (max_match/10, f"Orta dimer oluşma riski (Eşleşme: {max_match} baz)")
        else:
            return (max_match/10, f"Yüksek dimer oluşma riski (Eşleşme: {max_match} baz)")
    
    def evaluate_primer(self, primer):
        """
        Primer kalitesini değerlendirir.
        
        Args:
            primer (str): Primer dizisi
            
        Returns:
            dict: Primer değerlendirme sonuçları
        """
        primer = primer.upper()
        
        # Temel değerlendirmeler
        length = len(primer)
        gc_content = self.calculate_gc_content(primer)
        tm = self.calculate_tm(primer)
        
        # İkincil yapı kontrolü
        secondary_structure = self.check_secondary_structure(primer)
        
        # Kendi kendine dimer kontrolü
        primer_dimer = self.check_primer_dimer(primer)
        
        # GC-clamp kontrolü (3' ucunda G veya C varlığı)
        gc_clamp_present = primer[-1] in ['G', 'C']
        
        # Homopolimer kontrolü (4 veya daha fazla aynı baz ardışık olmamalı)
        homopolymer_run = bool(re.search(r'([ATGC])\1{3,}', primer))
        
        # Değerlendirme sonuçları
        results = {
            "length": {
                "value": length,
                "ideal": self.min_length <= length <= self.max_length,
                "message": f"Uzunluk: {length} baz çifti" + 
                          (", ideal aralıkta" if self.min_length <= length <= self.max_length 
                           else ", ideal aralık dışında")
            },
            "gc_content": {
                "value": gc_content,
                "ideal": self.min_gc <= gc_content <= self.max_gc,
                "message": f"GC içeriği: %{gc_content}" +
                          (", ideal aralıkta" if self.min_gc <= gc_content <= self.max_gc
                           else ", ideal aralık dışında")
            },
            "tm": {
                "value": tm,
                "ideal": self.min_tm <= tm <= self.max_tm,
                "message": f"Erime sıcaklığı (Tm): {tm}°C" +
                          (", ideal aralıkta" if self.min_tm <= tm <= self.max_tm
                           else ", ideal aralık dışında")
            },
            "secondary_structure": {
                "risk": secondary_structure[0],
                "message": secondary_structure[1]
            },
            "primer_dimer": {
                "risk": primer_dimer[0],
                "message": primer_dimer[1]
            },
            "gc_clamp": {
                "present": gc_clamp_present,
                "message": "3' ucunda G veya C bulunuyor" if gc_clamp_present 
                           else "3' ucunda G veya C bulunmuyor (GC-clamp yok)"
            },
            "homopolymer": {
                "present": homopolymer_run,
                "message": "Homopolimer dizileri bulunuyor (4+ aynı baz)" if homopolymer_run
                           else "Homopolimer dizisi tespit edilmedi"
            }
        }
        
        # Genel değerlendirme skoru (0-100)
        score = 100
        
        # İdeal olmayan durumlar için puanlardan düşürelim
        if not results["length"]["ideal"]:
            score -= 10
        if not results["gc_content"]["ideal"]:
            score -= 15
        if not results["tm"]["ideal"]:
            score -= 15
        
        # İkincil yapı ve dimer riski için puan düşürme
        score -= results["secondary_structure"]["risk"] * 20
        score -= results["primer_dimer"]["risk"] * 20
        
        if not results["gc_clamp"]["present"] and self.gc_clamp:
            score -= 10
            
        if results["homopolymer"]["present"]:
            score -= 20
            
        # Skoru 0-100 aralığında sınırla
        score = max(0, min(100, score))
        results["score"] = round(score)
        
        return results
    
    def evaluate_primer_pair(self, forward_primer, reverse_primer):
        """
        Primer çiftinin uyumluluğunu değerlendirir.
        
        Args:
            forward_primer (str): İleri primer dizisi
            reverse_primer (str): Geri primer dizisi
            
        Returns:
            dict: Primer çifti değerlendirme sonuçları
        """
        # Her bir primeri ayrı ayrı değerlendir
        forward_eval = self.evaluate_primer(forward_primer)
        reverse_eval = self.evaluate_primer(reverse_primer)
        
        # Tm farkı kontrolü
        forward_tm = forward_eval["tm"]["value"]
        reverse_tm = reverse_eval["tm"]["value"]
        tm_diff = abs(forward_tm - reverse_tm)
        tm_compatible = tm_diff <= 5
        
        # Primerler arası dimer kontrolü
        primer_dimer = self.check_primer_dimer(forward_primer, reverse_primer)
        
        # Çift değerlendirmesi
        results = {
            "forward_primer": forward_eval,
            "reverse_primer": reverse_eval,
            "tm_difference": {
                "value": tm_diff,
                "compatible": tm_compatible,
                "message": f"Tm farkı: {tm_diff}°C" +
                          (", uyumlu" if tm_compatible else ", çok farklı (5°C'den az olmalı)")
            },
            "primer_dimer": {
                "risk": primer_dimer[0],
                "message": primer_dimer[1]
            }
        }
        
        # Çift için genel uyumluluk skoru (0-100)
        pair_score = (forward_eval["score"] + reverse_eval["score"]) / 2
        
        # Tm farkı uyumlu değilse puan düşür
        if not tm_compatible:
            pair_score -= tm_diff * 2
            
        # Dimer riski için puan düşür
        pair_score -= results["primer_dimer"]["risk"] * 25
        
        # Skoru 0-100 aralığında sınırla
        pair_score = max(0, min(100, pair_score))
        results["pair_score"] = round(pair_score)
        
        return results
    
    def suggest_primers(self, template_sequence, target_length=None):
        """
        Verilen DNA şablonu için uygun primer çifti önerir.
        
        Args:
            template_sequence (str): Hedef DNA şablonu
            target_length (int, optional): Hedeflenen amplikon uzunluğu
            
        Returns:
            dict: Önerilen primer çiftleri ve değerlendirmeleri
        """
        # Bu metod, basit bir primer önerisi sunuyor
        # Daha gelişmiş öneri algoritmaları için daha kapsamlı bir analiz gerekir
        
        template = template_sequence.upper()
        
        if not target_length:
            target_length = min(500, len(template) - 40)  # Varsayılan hedef uzunluk
            
        if target_length < 40 or target_length > len(template) - 40:
            return {"error": "Geçersiz hedef uzunluk"}
        
        # Potansiyel primer başlangıç pozisyonları
        forward_start = 0
        reverse_start = len(template) - target_length - 20
        
        # Önerilen primer uzunluğu
        primer_length = 20
        
        # Potansiyel primerler listesi
        forward_candidates = []
        reverse_candidates = []
        
        # İleri primer adayları
        for i in range(forward_start, forward_start + 20):
            if i + primer_length <= len(template):
                candidate = template[i:i+primer_length]
                forward_candidates.append(candidate)
        
        # Geri primer adayları (reverse complement olarak)
        for i in range(reverse_start, reverse_start + 20):
            if i + primer_length <= len(template):
                candidate = self.reverse_complement(template[i:i+primer_length])
                reverse_candidates.append(candidate)
        
        # Her kombinasyonu değerlendir ve en iyi çifti bul
        best_pair = None
        best_score = 0
        
        for forward in forward_candidates:
            for reverse in reverse_candidates:
                eval_result = self.evaluate_primer_pair(forward, reverse)
                if eval_result["pair_score"] > best_score:
                    best_score = eval_result["pair_score"]
                    best_pair = {
                        "forward": forward,
                        "reverse": reverse,
                        "evaluation": eval_result,
                        "product_length": target_length
                    }
        
        if best_pair:
            return {"success": True, "primers": best_pair}
        else:
            return {"success": False, "error": "Uygun primer çifti bulunamadı"}
    
    def complement(self, sequence):
        """
        DNA dizisinin tamamlayıcısını döndürür.
        
        Args:
            sequence (str): DNA dizisi
            
        Returns:
            str: Tamamlayıcı DNA dizisi
        """
        comp_dict = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 
                     'a': 't', 't': 'a', 'g': 'c', 'c': 'g'}
        return ''.join(comp_dict.get(base, base) for base in sequence)
    
    def reverse_complement(self, sequence):
        """
        DNA dizisinin ters tamamlayıcısını döndürür.
        
        Args:
            sequence (str): DNA dizisi
            
        Returns:
            str: Ters tamamlayıcı DNA dizisi
        """
        return self.complement(sequence)[::-1] 