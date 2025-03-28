"""
PCR protokollerini oluşturan ve formatlayan modül.
"""

import json
from datetime import datetime


class PCRProtocolGenerator:
    """PCR protokollerini oluşturmak için ana sınıf."""
    
    def __init__(self, optimizer=None):
        """
        PCRProtocolGenerator sınıfı için başlatıcı.
        
        Args:
            optimizer: PCROptimizer nesnesi (opsiyonel)
        """
        self.optimizer = optimizer
    
    def generate_protocol(self, protocol=None, **kwargs):
        """
        Verilen parametrelere göre PCR protokolü oluşturur.
        
        Args:
            protocol (dict, optional): Doğrudan kullanılacak protokol objesi
            **kwargs: PCR parametreleri (optimizer için)
            
        Returns:
            dict: Protokol bilgisi
        """
        if protocol:
            return protocol
        
        if self.optimizer:
            return self.optimizer.create_complete_protocol(**kwargs)
            
        # Optimizer yoksa ve protokol verilmemişse hata ver
        if not protocol:
            raise ValueError("Protokol verilmedi ve optimizer tanımlanmadı")
    
    def format_time(self, seconds):
        """
        Saniye cinsinden süreyi okunabilir formata dönüştürür.
        
        Args:
            seconds: Saniye cinsinden süre
            
        Returns:
            str: Formatlanmış süre (dakika:saniye)
        """
        if seconds == "indefinite":
            return "Süresiz"
            
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        
        if minutes > 0:
            return f"{minutes} dk {remaining_seconds} sn"
        else:
            return f"{remaining_seconds} sn"
    
    def protocol_to_text(self, protocol):
        """
        Protokolü metin formatına dönüştürür.
        
        Args:
            protocol (dict): Protokol bilgisi
            
        Returns:
            str: Formatlanmış protokol metni
        """
        text = "# PCR Protokolü\n\n"
        
        # Başlangıç denatürasyonu
        text += "## Başlangıç Denatürasyonu\n"
        text += f"- Sıcaklık: {protocol['initial_denaturation']['temperature']}°C\n"
        text += f"- Süre: {self.format_time(protocol['initial_denaturation']['time'])}\n\n"
        
        # Döngüler
        text += f"## Döngüler (x{protocol['cycles']['count']})\n"
        
        # Denatürasyon
        text += "### Denatürasyon\n"
        text += f"- Sıcaklık: {protocol['cycles']['denaturation']['temperature']}°C\n"
        text += f"- Süre: {self.format_time(protocol['cycles']['denaturation']['time'])}\n\n"
        
        # Bağlanma
        text += "### Bağlanma (Annealing)\n"
        text += f"- Sıcaklık: {protocol['cycles']['annealing']['temperature']}°C\n"
        text += f"- Süre: {self.format_time(protocol['cycles']['annealing']['time'])}\n\n"
        
        # Uzama
        text += "### Uzama (Extension)\n"
        text += f"- Sıcaklık: {protocol['cycles']['extension']['temperature']}°C\n"
        text += f"- Süre: {self.format_time(protocol['cycles']['extension']['time'])}\n\n"
        
        # Son uzama
        text += "## Son Uzama\n"
        text += f"- Sıcaklık: {protocol['final_extension']['temperature']}°C\n"
        text += f"- Süre: {self.format_time(protocol['final_extension']['time'])}\n\n"
        
        # Saklama
        text += "## Saklama\n"
        text += f"- Sıcaklık: {protocol['hold']['temperature']}°C\n"
        text += f"- Süre: {self.format_time(protocol['hold']['time'])}\n\n"
        
        # Ek bilgiler
        if "gc_content" in protocol:
            text += f"GC İçeriği: %{protocol['gc_content']}\n\n"
            
        # Toplam süre
        total_time = protocol['initial_denaturation']['time']
        total_time += protocol['cycles']['count'] * (
            protocol['cycles']['denaturation']['time'] +
            protocol['cycles']['annealing']['time'] +
            protocol['cycles']['extension']['time']
        )
        total_time += protocol['final_extension']['time']
        
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        seconds = total_time % 60
        
        time_str = ""
        if hours > 0:
            time_str += f"{hours} saat "
        if minutes > 0:
            time_str += f"{minutes} dakika "
        if seconds > 0:
            time_str += f"{seconds} saniye"
            
        text += f"Tahmini Toplam Süre: {time_str.strip()}\n"
        
        return text
    
    def protocol_to_json(self, protocol):
        """
        Protokolü JSON formatına dönüştürür.
        
        Args:
            protocol (dict): Protokol bilgisi
            
        Returns:
            str: JSON formatında protokol
        """
        return json.dumps(protocol, indent=2, ensure_ascii=False)
    
    def protocol_to_csv(self, protocol):
        """
        Protokolü CSV formatına dönüştürür.
        
        Args:
            protocol (dict): Protokol bilgisi
            
        Returns:
            str: CSV formatında protokol
        """
        csv_lines = ["Adım,Sıcaklık (°C),Süre,Döngü"]
        
        # Başlangıç denatürasyonu
        csv_lines.append(
            f"Başlangıç Denatürasyonu,{protocol['initial_denaturation']['temperature']},"
            f"{protocol['initial_denaturation']['time']},1"
        )
        
        # Döngüler
        csv_lines.append(
            f"Denatürasyon,{protocol['cycles']['denaturation']['temperature']},"
            f"{protocol['cycles']['denaturation']['time']},{protocol['cycles']['count']}"
        )
        
        csv_lines.append(
            f"Bağlanma,{protocol['cycles']['annealing']['temperature']},"
            f"{protocol['cycles']['annealing']['time']},{protocol['cycles']['count']}"
        )
        
        csv_lines.append(
            f"Uzama,{protocol['cycles']['extension']['temperature']},"
            f"{protocol['cycles']['extension']['time']},{protocol['cycles']['count']}"
        )
        
        # Son uzama
        csv_lines.append(
            f"Son Uzama,{protocol['final_extension']['temperature']},"
            f"{protocol['final_extension']['time']},1"
        )
        
        # Saklama
        csv_lines.append(
            f"Saklama,{protocol['hold']['temperature']},{protocol['hold']['time']},1"
        )
        
        return "\n".join(csv_lines)
    
    def generate_report(self, protocol, parameters=None, format="text"):
        """
        Protokol raporu oluşturur.
        
        Args:
            protocol (dict): Protokol bilgisi
            parameters (dict, optional): Giriş parametreleri
            format (str): Çıktı formatı ("text", "json", "csv")
            
        Returns:
            str: Formatlanmış protokol raporu
        """
        if format == "json":
            return self.protocol_to_json(protocol)
        elif format == "csv":
            return self.protocol_to_csv(protocol)
        
        # Varsayılan olarak metin formatı
        report = self.protocol_to_text(protocol)
        
        # Giriş parametreleri verilmişse ekle
        if parameters:
            report += "\n## Giriş Parametreleri\n"
            for key, value in parameters.items():
                readable_key = key.replace("_", " ").capitalize()
                report += f"- {readable_key}: {value}\n"
                
        # Oluşturulma tarihi
        report += f"\nOluşturulma Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        
        return report 