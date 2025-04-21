# Awora-FLX Nükleer Reaktör Güvenlik Analiz Projesi

[![Lisans](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-%3E=3.6-blue.svg)

Bu proje, nükleer reaktörlerin güvenlik analizini gerçekleştirmek amacıyla geliştirilmiş bir araçtır. Awora-FLX formülünü temel alarak, reaktördeki çeşitli fiziksel parametreleri (sıcaklık, basınç, nötron akışı, radyasyon) analiz eder ve potansiyel risk seviyesini değerlendirir.

## İçindekiler

1.  [Giriş](#giriş)
2.  [Awora-FLX Formülü](#awora-flx-formülü)
3.  [Proje Mimarisi](#proje-mimarisi)
4.  [Kurulum](#kurulum)
5.  [Kullanım](#kullanım)
6.  [Çıktı Analizi](#çıktı-analizi)
7.  [Katkıda Bulunma](#katkıda-bulunma)
8.  [Lisans](#lisans)

## 1. Giriş

Nükleer reaktörlerin güvenliği, enerji üretimi süreçlerinin en kritik yönlerinden biridir. Bu proje, reaktörlerin işletimi sırasında ortaya çıkabilecek potansiyel tehlikeleri erken aşamada tespit etmek ve analiz etmek için geliştirilmiştir. Awora-FLX formülünü kullanarak, reaktördeki temel fiziksel değişkenlerin etkileşimini modelleyerek risk değerlendirmesi sunar.

## 2. Awora-FLX Formülü

Awora-FLX formülü, reaktörün termal (TS), basınç (BS), nötron (NS) ve radyasyon (RS) skorlarını dikkate alarak genel bir risk değerlendirme skoru (G) üretir. Temel diferansiyel denklemler şunlardır:

* **Termal:** $\frac{dTS}{dt} = DT \nabla^2 TS + \alpha \cdot TS \cdot NS - \beta \cdot NS$
* **Basınç:** $\frac{dBS}{dt} = \gamma \cdot (\Delta P + \lambda \cdot TS) - \delta \cdot BS^2$
* **Nötron:** $\frac{dNS}{dt} = \epsilon + \phi - \zeta \cdot NS \cdot TS$
* **Radyasyon:** $\frac{dRS}{dt} = \eta \cdot R_{dose} - \theta \cdot RS$

Genel risk skoru (G) ise ağırlıklandırılmış bir kombinasyonla hesaplanır:

$G = w_{TS} \cdot f(TS) + w_{BS} \cdot g(BS) + w_{NS} \cdot h(NS) + w_{RS} \cdot k(RS)$

Bu formüldeki parametreler ve fonksiyonlar, modellenen reaktörün özelliklerine ve çalışma koşullarına göre ayarlanır.

## 3. Proje Mimarisi

Proje, temel olarak üç ana katmandan oluşmaktadır:

* **`formulasa.py`:** Awora-FLX formüllerini ve diferansiyel denklemleri sayısal olarak çözen fonksiyonları içerir. `scipy.integrate.solve_ivp` kütüphanesini kullanır.
* **`core.py`:** Ham veriyi (`input.json`) ve yapılandırma bilgilerini (`config.json`) okur, `formulasa.py`'ı çağırarak analiz sonuçlarını elde eder.
* **`calculator.py`:** `core.py`'dan gelen analiz sonuçlarını düzenler ve `output.json` dosyasına yazar.

## 4. Kurulum

1.  **Python Sürümü:** Bu proje Python 3.6 veya üzeri ile çalışır.
2.  **Gerekli Kütüphaneler:**
    ```bash
    pip install -r requirements.txt
    ```
    `requirements.txt` dosyası, projenin bağımlı olduğu kütüphaneleri (şu anda sadece `scipy`) içerir.

## 5. Kullanım

1.  **Yapılandırma:** `config.json` dosyasını projenin gereksinimlerine göre düzenleyin. Bu dosya, Awora-FLX formülü parametrelerini ve simülasyon ayarlarını içerir. Örnek bir `config.json` dosyası için [`config.json`](config.json) dosyasına bakın.
2.  **Girdi Verisi:** Analiz etmek istediğiniz reaktör verilerini `input.json` dosyasına uygun formatta girin. Şu anda beklenen temel format (örnek):
    ```json
    {
        "TS": 1.05,
        "BS": 1.1,
        "NS": 1.02,
        "RS": 0.95,
        "dP": 0.01,
        "Radyasyon_Dozu": 0.001
    }
    ```
    Gelecekte zaman serisi verileri için destek eklenecektir.
3.  **Çalıştırma:** Projeyi çalıştırmak için `core.py` dosyasını çalıştırın:
    ```bash
    python core.py
    ```
4.  **Çıktı:** Analiz sonuçları `output.json` dosyasına yazılacaktır.

## 6. Çıktı Analizi

`output.json` dosyası, simülasyonun zaman serisi boyunca hesaplanan skorları (TS, BS, NS, RS) ve genel risk değerini (G) içerir.

```json
{
  "ham_veri_konumu": "input.json",
  "zaman_serisi": [
    {
      "zaman": "0.00",
      "TS": "1.0500",
      "BS": "1.1000",
      "NS": "1.0200",
      "RS": "0.9500",
      "G": "1.0100"
    },
    // ... diğer zaman noktaları
  ]
}
