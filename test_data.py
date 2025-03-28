"""
PCR Optimizer için test verileri.
Bu veriler, PCR optimize edici için örnek girdiler içerir.
"""

# Kısa PCR amplifikasyonu için örnek veri
SHORT_PCR = {
    "forward_primer": "ATGCTAGCTAGCTAGCTAGT",
    "reverse_primer": "TAGCTAGCTAGCTAGCATCG",
    "template_length": 500,
    "template_gc": 52.3,
    "template_concentration": 10,
    "target_yield": 100,
    "is_diagnostic": False
}

# Uzun PCR amplifikasyonu için örnek veri
LONG_PCR = {
    "forward_primer": "GCTACGTAGCTAGCGCTATCGATCG",
    "reverse_primer": "AGCTGATCGATCGATGGCTACGTAT",
    "template_length": 3500,
    "template_gc": 45.8,
    "template_concentration": 5,
    "target_yield": 200,
    "is_diagnostic": False
}

# GC-zengin şablon için örnek veri
GC_RICH_PCR = {
    "forward_primer": "GCGCGGCGCGGCGCTAGCTAG",
    "reverse_primer": "GCGCGCTAGCTAGCGCGCTAG",
    "template_length": 800,
    "template_gc": 68.5,
    "template_concentration": 15,
    "target_yield": 150,
    "is_diagnostic": False
}

# AT-zengin şablon için örnek veri
AT_RICH_PCR = {
    "forward_primer": "ATAATATATATAATATATATAT",
    "reverse_primer": "TATTATATATATTATATATTA",
    "template_length": 600,
    "template_gc": 28.6,
    "template_concentration": 12,
    "target_yield": 120,
    "is_diagnostic": False
}

# Tanısal PCR için örnek veri
DIAGNOSTIC_PCR = {
    "forward_primer": "ACGTACGTACGTACGTACGT",
    "reverse_primer": "TGCATGCATGCATGCATGCA",
    "template_length": 250,
    "template_gc": 50.0,
    "template_concentration": 2,
    "target_yield": 50,
    "is_diagnostic": True
}

# Koloni PCR için örnek veri
COLONY_PCR = {
    "forward_primer": "TGACTAGCTAGCTAGCTAGC",
    "reverse_primer": "GCTAGCTAGCTAGCTAGCTA",
    "template_length": 1200,
    "template_gc": 55.3,
    "template_concentration": 0.5,
    "target_yield": 20,
    "is_diagnostic": True
}

# Primer dizileri kullanımı için örnek sekanslar
EXAMPLE_SEQUENCES = {
    "human_beta_actin_f": "AGAGCTACGAGCTGCCTGAC",
    "human_beta_actin_r": "AGCACTGTGTTGGCGTACAG",
    "ecoli_16s_f": "AGAGTTTGATCCTGGCTCAG",
    "ecoli_16s_r": "GGTTACCTTGTTACGACTT",
    "gfp_f": "ATGGTGAGCAAGGGCGAG",
    "gfp_r": "TTACTTGTACAGCTCGTCCATG",
    "t7_promoter": "TAATACGACTCACTATAGGG",
    "m13_forward": "GTAAAACGACGGCCAGT",
    "m13_reverse": "CAGGAAACAGCTATGACC"
}

# Daha karmaşık PCR protokolleri için örnek veri
COMPLEX_PCR_EXAMPLES = [
    {
        "name": "Two-step PCR",
        "forward_primer": "GCGCTAGCTAGCTCGATATCGCTACG",
        "reverse_primer": "CGCGATCGATCGAGCTATATCGACGC",
        "template_length": 2000,
        "template_gc": 58.2,
        "template_concentration": 8,
        "target_yield": 300,
        "is_diagnostic": False,
        "notes": "İki adımlı PCR, yüksek Tm'li primerler için bağlanma ve uzama adımlarını birleştirir."
    },
    {
        "name": "Touchdown PCR",
        "forward_primer": "AGCTCGATCGATCGTACGATGCTAGC",
        "reverse_primer": "CGTAGCTAGCTAGCGCGCTCGATCGC",
        "template_length": 1500,
        "template_gc": 62.5,
        "template_concentration": 7,
        "target_yield": 250,
        "is_diagnostic": False,
        "notes": "Touchdown PCR, ilk birkaç döngüde bağlanma sıcaklığını kademeli olarak düşürür."
    }
]

# Hızlı test için minimal veri seti
MINIMAL_TEST_DATA = {
    "forward_primer": "ACGTACGTACGT",
    "reverse_primer": "TGCATGCATGCA",
    "template_length": 300
} 