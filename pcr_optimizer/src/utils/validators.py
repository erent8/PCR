"""
PCR optimizasyon uygulaması için girdi doğrulama fonksiyonları.
"""

import re
from .helpers import is_valid_dna_sequence


class PCRValidationError(Exception):
    """PCR validasyon hatası için özel istisna sınıfı."""
    pass


def validate_dna_sequence(sequence, field_name="DNA dizisi"):
    """
    DNA dizisini doğrular.
    
    Args:
        sequence (str): Doğrulanacak DNA dizisi
        field_name (str): Hata mesajında kullanılacak alan adı
        
    Returns:
        str: Doğrulanmış DNA dizisi (büyük harfle)
        
    Raises:
        PCRValidationError: Dizi geçerli değilse
    """
    if not sequence:
        raise PCRValidationError(f"{field_name} boş olamaz.")
        
    # Boşlukları kaldır
    sequence = sequence.replace(" ", "").replace("\n", "").replace("\t", "")
    
    if not is_valid_dna_sequence(sequence):
        raise PCRValidationError(
            f"{field_name} yalnızca A, T, G, C, N karakterlerini içerebilir."
        )
        
    return sequence.upper()


def validate_numeric_value(value, field_name, min_value=None, max_value=None):
    """
    Sayısal değeri doğrular.
    
    Args:
        value: Doğrulanacak değer
        field_name (str): Hata mesajında kullanılacak alan adı
        min_value: İzin verilen minimum değer
        max_value: İzin verilen maksimum değer
        
    Returns:
        float or int: Doğrulanmış sayısal değer
        
    Raises:
        PCRValidationError: Değer geçerli değilse
    """
    try:
        if isinstance(value, str):
            value = value.strip()
            # Virgül yerine nokta kullan (Türkçe biçim)
            value = value.replace(",", ".")
            
        num_value = float(value)
        
        # Tam sayı kontrolü
        if num_value.is_integer():
            num_value = int(num_value)
            
    except (ValueError, TypeError):
        raise PCRValidationError(f"{field_name} geçerli bir sayı olmalıdır.")
        
    if min_value is not None and num_value < min_value:
        raise PCRValidationError(f"{field_name} en az {min_value} olmalıdır.")
        
    if max_value is not None and num_value > max_value:
        raise PCRValidationError(f"{field_name} en fazla {max_value} olmalıdır.")
        
    return num_value


def validate_primer(primer, primer_type="Primer"):
    """
    Primer dizisini doğrular.
    
    Args:
        primer (str): Doğrulanacak primer dizisi
        primer_type (str): Primer tipi (ör. "İleri primer", "Geri primer")
        
    Returns:
        str: Doğrulanmış primer dizisi (büyük harfle)
        
    Raises:
        PCRValidationError: Primer geçerli değilse
    """
    if not primer:
        raise PCRValidationError(f"{primer_type} boş olamaz.")
        
    # Boşlukları kaldır
    primer = primer.replace(" ", "").replace("\n", "").replace("\t", "")
    
    if not is_valid_dna_sequence(primer):
        raise PCRValidationError(
            f"{primer_type} yalnızca A, T, G, C, N karakterlerini içerebilir."
        )
        
    # Primer uzunluğu genellikle 15-30 baz arasındadır
    if len(primer) < 15:
        raise PCRValidationError(
            f"{primer_type} çok kısa (en az 15 baz olmalıdır)."
        )
        
    if len(primer) > 40:
        raise PCRValidationError(
            f"{primer_type} çok uzun (en fazla 40 baz olmalıdır)."
        )
        
    return primer.upper()


def validate_template_length(length):
    """
    Şablon DNA uzunluğunu doğrular.
    
    Args:
        length: Doğrulanacak uzunluk değeri
        
    Returns:
        int: Doğrulanmış uzunluk değeri
        
    Raises:
        PCRValidationError: Uzunluk geçerli değilse
    """
    return validate_numeric_value(
        length, 
        "Şablon uzunluğu", 
        min_value=50, 
        max_value=50000
    )


def validate_cycle_number(cycles):
    """
    PCR döngü sayısını doğrular.
    
    Args:
        cycles: Doğrulanacak döngü sayısı
        
    Returns:
        int: Doğrulanmış döngü sayısı
        
    Raises:
        PCRValidationError: Döngü sayısı geçerli değilse
    """
    return validate_numeric_value(
        cycles, 
        "Döngü sayısı", 
        min_value=15, 
        max_value=45
    )


def validate_temperature(temp, field_name="Sıcaklık"):
    """
    Sıcaklık değerini doğrular.
    
    Args:
        temp: Doğrulanacak sıcaklık değeri
        field_name (str): Hata mesajında kullanılacak alan adı
        
    Returns:
        float: Doğrulanmış sıcaklık değeri
        
    Raises:
        PCRValidationError: Sıcaklık geçerli değilse
    """
    return validate_numeric_value(
        temp, 
        field_name, 
        min_value=4, 
        max_value=105
    )


def validate_time(time_value, field_name="Süre"):
    """
    Süre değerini doğrular.
    
    Args:
        time_value: Doğrulanacak süre değeri (saniye)
        field_name (str): Hata mesajında kullanılacak alan adı
        
    Returns:
        int: Doğrulanmış süre değeri
        
    Raises:
        PCRValidationError: Süre geçerli değilse
    """
    return validate_numeric_value(
        time_value, 
        field_name, 
        min_value=1, 
        max_value=7200
    )


def validate_concentration(conc, field_name="Konsantrasyon"):
    """
    Konsantrasyon değerini doğrular.
    
    Args:
        conc: Doğrulanacak konsantrasyon değeri
        field_name (str): Hata mesajında kullanılacak alan adı
        
    Returns:
        float: Doğrulanmış konsantrasyon değeri
        
    Raises:
        PCRValidationError: Konsantrasyon geçerli değilse
    """
    return validate_numeric_value(
        conc, 
        field_name, 
        min_value=0, 
        max_value=1000
    ) 