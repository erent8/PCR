"""
PCR optimizasyon uygulaması için yardımcı fonksiyonlar.
"""

import re


def is_valid_dna_sequence(sequence):
    """
    Verilen dizinin geçerli bir DNA dizisi olup olmadığını kontrol eder.
    
    Args:
        sequence (str): Kontrol edilecek DNA dizisi
        
    Returns:
        bool: Dizi geçerli ise True, değilse False
    """
    if not sequence:
        return False
        
    # Dizi yalnızca A, T, G, C, N içermeli (büyük/küçük harf duyarsız)
    pattern = r'^[ATGCNatgcn]+$'
    return bool(re.match(pattern, sequence))


def format_dna_sequence(sequence, width=60):
    """
    DNA dizisini okunabilir bir formatta biçimlendirir.
    
    Args:
        sequence (str): Formatlanacak DNA dizisi
        width (int): Her satırdaki maksimum karakter sayısı
        
    Returns:
        str: Formatlanmış DNA dizisi
    """
    if not sequence:
        return ""
        
    sequence = sequence.upper()
    
    # Diziyi belirtilen genişlikte alt dizilere böl
    formatted_seq = [sequence[i:i+width] for i in range(0, len(sequence), width)]
    
    # Satır numaralarıyla birlikte formatla
    result = []
    for i, line in enumerate(formatted_seq):
        position = i * width + 1
        result.append(f"{position:6d} {line}")
        
    return "\n".join(result)


def estimate_pcr_product_size(forward_primer, reverse_primer, template_length=None):
    """
    PCR ürün boyutunu tahmin eder.
    
    Args:
        forward_primer (str): İleri primer dizisi
        reverse_primer (str): Geri primer dizisi
        template_length (int, optional): Şablon DNA uzunluğu
        
    Returns:
        str: Tahmin edilen PCR ürün boyutu açıklaması
    """
    if not forward_primer or not reverse_primer:
        return "Primer dizileri belirtilmediği için ürün boyutu tahmin edilemiyor."
        
    if template_length:
        # Ortalama bir değer olarak tahmin et
        primer_length = (len(forward_primer) + len(reverse_primer)) / 2
        estimated_size = int(template_length - primer_length)
        
        return f"Tahmini PCR ürün boyutu: ~{estimated_size} baz çifti"
    else:
        return "Şablon uzunluğu belirtilmediği için kesin boyut tahmin edilemiyor."


def convert_seconds_to_time_format(seconds):
    """
    Saniye cinsinden süreyi saat:dakika:saniye formatına dönüştürür.
    
    Args:
        seconds (int): Saniye cinsinden süre
        
    Returns:
        str: hh:mm:ss formatında süre
    """
    if seconds == "indefinite":
        return "∞"
        
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def generate_filename(prefix, extension, timestamp=True):
    """
    Dosya adı oluşturur.
    
    Args:
        prefix (str): Dosya adı öneki
        extension (str): Dosya uzantısı
        timestamp (bool): Zaman damgası eklensin mi
        
    Returns:
        str: Oluşturulan dosya adı
    """
    import datetime
    
    if timestamp:
        now = datetime.datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp_str}.{extension}"
    else:
        filename = f"{prefix}.{extension}"
        
    return filename 