# Awora-Reactor-CS

## Proje Hakkında
Awora-Reactor-CS, nükleer reaktör simülasyonu ve risk analizi için geliştirilmiş, Python tabanlı bir hesaplama ve analiz aracıdır. Proje, Awora-FLX çekirdeği ve matematiksel modelleriyle verilen ham veriler ve yapılandırma dosyası üzerinden çeşitli skorlar (TS, BS, NS, RS) ve risk değeri (G) hesaplar. Tüm işlevler tek bir dosyada (`awora_reactor.py`) toplanmıştır.

## Awora-FLX Nedir?
Awora-FLX, reaktör davranışını ve güvenliğini modellemek için geliştirilmiş bir matematiksel modeldir. Farklı fiziksel parametreleri (termal, basınç, nötron, radyasyon) ve bunların zamana bağlı değişimlerini diferansiyel denklemlerle simüle eder. Sonuç olarak, reaktörün genel risk skorunu (G) ve zamana bağlı diğer skorları üretir.

## Temel Özellikler
- Tek dosya ile kolay kurulum ve kullanım
- JSON tabanlı esnek veri ve konfigürasyon girişi
- Aşamalı hesaplama ve detaylı loglama desteği
- Sonuçları hem dosyaya hem ekrana yazdırabilme
- Test fonksiyonu ile hızlı doğrulama

## Dosya Yapısı
- `awora_reactor.py` : Ana uygulama dosyası
- `KULLANIM_KILAVUZU.txt` : Detaylı kullanım rehberi
- `config.json` : Yapılandırma dosyası (parametreler ve simülasyon ayarları)
- `input.json` : Ham veri dosyası (simülasyon girdileri)
- `output.json` : Sonuçların kaydedileceği dosya
- `awora_reactor.log` : Log dosyası
- (isteğe bağlı) `asama_log.json` : Aşamalı hesaplama log dosyası

## Kurulum
1. Python 3.8+ yüklü olmalı.
2. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

## Kullanım
```bash
python awora_reactor.py --config config.json --data input.json --output output.json
```
Ekstra seçenekler:
- `--print` : Sonuçları ekrana da yazdırır
- `--step-log dosya.json` : Her hesaplama adımını JSON olarak ayrı dosyaya kaydeder

Test için:
```bash
python awora_reactor.py test
```

## Girdi Dosyası Örneği
`config.json` ve `input.json` örnekleri için KULLANIM_KILAVUZU.txt dosyasına bakınız.

## Loglama
- Tüm bilgi, uyarı ve hata mesajları `awora_reactor.log` dosyasına kaydedilir.
- Aşamalı hesaplama için her adımda ara değerler ayrı bir JSON dosyasına kaydedilebilir.

---

## Lisans
Bu proje hem [MIT Lisansı](./LICENSE-MIT.md) hem de [Ticari Lisans](./LICENSE-COMMERCIAL.md) ile sunulmaktadır. Kullanım amacınıza göre uygun lisansı inceleyiniz.

- [MIT License](./LICENSE-MIT.md)
- [Ticari Lisans](./LICENSE-COMMERCIAL.md)

## Gizlilik
Kullanıcı verisi toplanmaz. Detaylar için [PRİVACY.md](./PRİVACY.md) dosyasına bakınız.

## İletişim
Her türlü soru, öneri veya ticari işbirliği için:
- E-posta: devranaktas153@gmail.com

---
