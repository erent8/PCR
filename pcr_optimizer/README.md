# PCR Optimizer

PCR (Polimeraz Zincir Reaksiyonu) deneylerinin optimizasyonu için geliştirilmiş bir yazılım aracı.

## Özellikler

- Sıcaklık döngülerini optimize etme
- DNA uzunluğuna göre reaksiyon süresini hesaplama
- Farklı DNA uzunlukları için özelleştirilmiş protokoller önerme
- Primer özellikleri analizi
- GC içeriği analizi
- Otomatik protokol oluşturma
- PDF rapor oluşturma

## Kurulum

Gereksinimler:
- Python 3.8 veya üzeri

Kurulum adımları:

```bash
# Depoyu klonlayın
git clone https://github.com/erent8/pcr-optimizer.git
cd pcr-optimizer

# Sanal ortam oluşturun (opsiyonel ama önerilir)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Gereksinimleri yükleyin
pip install -r requirements.txt

# Uygulamayı çalıştırın
python src/app.py
```

## Kullanım

Uygulamayı çalıştırdıktan sonra, tarayıcınızda `http://localhost:5000` adresine giderek web arayüzüne erişebilirsiniz.

1. DNA uzunluğunu veya dizisini girin
2. Primer bilgilerini girin (opsiyonel)
3. "Optimize Et" düğmesine tıklayın
4. Önerilen PCR protokolünü görüntüleyin

## Katkıda Bulunma

1. Bu depoyu forklayın
2. Yeni bir özellik dalı oluşturun (`git checkout -b yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: özet'`)
4. Dalınıza push yapın (`git push origin yeni-ozellik`)
5. Bir Pull Request oluşturun

## Lisans

Bu proje [MIT](LICENSE) lisansı altında lisanslanmıştır. 