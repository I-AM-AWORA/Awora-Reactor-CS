# Awora-FLX Projesi

[![Lisans](https://img.shields.io/badge/License-MIT%20OR%20Commercial-yellowgreen.svg)](LICENSE.md)
![Python](https://img.shields.io/badge/Python-%3E=3.6-blue.svg)

Bu proje, nükleer reaktörlerin güvenlik analizini gerçekleştirmek amacıyla geliştirilmiş bir araçtır. Awora-FLX formülünü temel alarak, reaktördeki çeşitli fiziksel parametreleri (Termal Skor (TS), Basınç Skoru (BS), Nötron Skoru (NS), Radyasyon Skoru (RS)) analiz eder ve potansiyel risk seviyesini (G) değerlendirir. Projenin geliştirilmesinde yapay zeka programları önemli bir asistan rolü oynamış, formüllerin oluşturulması ve kodun geliştirilmesi süreçlerinde Devran Durmaz'a yardımcı olmuştur.

### Yapay Zeka Asistanının Rolü

Bu projenin geliştirilmesi sürecinde, yapay zeka tabanlı programlar Devran Durmaz'a önemli ölçüde yardımcı olmuştur. Bu programlar, Awora-FLX formüllerinin oluşturulması, matematiksel modellemenin yapılması ve kodun geliştirilmesi gibi çeşitli aşamalarda Devran Durmaz'a destek sağlamıştır. Ancak, projenin temel fikirleri, konsepti ve nihai tasarımı Devran Durmaz'a aittir. Yapay zeka asistanları bir araç olarak kullanılmış olup, projenin yaratıcısı ve sahibi Devran Durmaz'dır.

## Lisans

Bu proje çift lisans altında yayınlanmaktadır:

* **Bireysel ve Açık Kaynak Kullanımı:** Kaynak kodu, [MIT Lisansı](#mit-lisansı) altında serbestçe kullanılabilir. Bu, ticari olmayan amaçlarla kullanım, inceleme, değiştirme ve dağıtmayı içerir.
* **Ticari Kullanım:** Yazılımın ve temel Awora-FLX formüllerinin ticari kullanımı özel koşullara tabidir. Daha fazla bilgi için lütfen bu belgenin altındaki "Ticari Kullanım" bölümünü inceleyin veya geliştiriciyle (Devran Durmaz) iletişime geçin.

## İçindekiler

1.  [Giriş](#giriş)
2.  [Awora-FLX Formülü ve Skorlar](#awora-flx-formülü-ve-skorlar)
3.  [Proje Mimarisi](#proje-mimarisi)
4.  [Kurulum](#kurulum)
5.  [Kullanım](#kullanım)
6.  [Çıktı Analizi](#çıktı-analizi)
7.  [Lisans Detayları](#lisans-detayları)
    * [MIT Lisansı](#mit-lisansı)
    * [Ticari Kullanım](#ticari-kullanım)
    * [Yapay Zeka Asistanının Rolü](#yapay-zeka-asistanının-rolü)

## 1. Giriş

Nükleer reaktörlerin güvenliği, enerji üretimi süreçlerinin en kritik yönlerinden biridir. Bu proje, reaktörlerin işletimi sırasında ortaya çıkabilecek potansiyel tehlikeleri erken aşamada tespit etmek ve analiz etmek için geliştirilmiştir. Awora-FLX formülünü kullanarak, reaktördeki temel fiziksel değişkenlerin etkileşimini modelleyerek risk değerlendirmesi sunar.

## 2. Awora-FLX Formülü ve Skorlar

Awora-FLX formülü, reaktörün dört temel skorunu dikkate alarak genel bir risk değerlendirme skoru (G) üretir:

* **Termal Skor (TS):** Reaktörün sıcaklık seviyesini ve değişimini ifade eder.
* **Basınç Skoru (BS):** Reaktör içindeki basınç seviyesini ve değişimini ifade eder.
* **Nötron Skoru (NS):** Reaktördeki nötron akışını ve yoğunluğunu ifade eder.
* **Radyasyon Skoru (RS):** Reaktörden yayılan radyasyon seviyesini ve dozunu ifade eder.

Bu skorlar arasındaki dinamik ilişkiler aşağıdaki temel diferansiyel denklemlerle modellenir:

* **Termal:** $\frac{dTS}{dt} = DT \nabla^2 TS + \alpha \cdot TS \cdot NS - \beta \cdot NS$
* **Basınç:** $\frac{dBS}{dt} = \gamma \cdot (\Delta P + \lambda \cdot TS) - \delta \cdot BS^2$
* **Nötron:** $\frac{dNS}{dt} = \epsilon + \phi - \zeta \cdot NS \cdot TS$
* **Radyasyon:** $\frac{dRS}{dt} = \eta \cdot R_{dose} - \theta \cdot RS$

Genel risk skoru (G) ise bu skorların ağırlıklandırılmış bir kombinasyonuyla hesaplanır:

$G = w_{TS} \cdot f(TS) + w_{BS} \cdot g(BS) + w_{NS} \cdot h(NS) + w_{RS} \cdot k(RS)$

Bu formüldeki parametreler ve fonksiyonlar, modellenen reaktörün özelliklerine ve çalışma koşullarına göre ayarlanır. Temel Awora-FLX formüllerinin fikri mülkiyeti Devran Durmaz'a aittir.

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

1.  **Yapılandırma:** `config.json` dosyasını projenin gereksinimlerine göre düzenleyin. Bu dosya, Awora-FLX formülü parametrelerini ve simülasyon ayarlarını içerir.
2.  **Girdi Verisi:** Analiz etmek istediğiniz reaktör verilerini `input.json` dosyasına uygun formatta girin.
3.  **Çalıştırma:** Projeyi çalıştırmak için `core.py` dosyasını çalıştırın:
    ```bash
    python core.py
    ```
4.  **Çıktı:** Analiz sonuçları `output.json` dosyasına yazılacaktır.

## 6. Çıktı Analizi

`output.json` dosyası, simülasyonun zaman serisi boyunca hesaplanan skorları (TS, BS, NS, RS) ve genel risk değerini (G) içerir. Detaylı çıktı formatı ve yorumlama bilgileri için lütfen ilgili belgelere başvurun.

## 7\. Lisans Detayları

Bu proje çift lisanslıdır: MIT Lisansı (açık kaynak ve bireysel kullanım için) ve Özel Ticari Lisans (ticari kullanım için).

### MIT Lisansı
### Ticari Kullanım

Awora-FLX Projesi'nin ve temel Awora-FLX formüllerinin ticari amaçlarla kullanımı özel koşullara tabidir. Ticari kullanım, Yazılımın veya temel formüllerin ticari ürünlerde veya hizmetlerde bütünleştirilmesini, doğrudan veya dolaylı olarak satışını, ticari faaliyetlerde kullanılmasını ve formüllerin analiz edilmesini veya patent başvurusuna konu edilmesini içerir.

Temel Awora-FLX formüllerinin fikri mülkiyeti Devran Durmaz'a aittir. Ticari kullanım için önceden yazılı izin alınması ve özel bir lisans anlaşması yapılması gerekmektedir.

Ticari lisans almak veya ticari kullanımınızın lisans gerektirip gerektirmediğini öğrenmek için lütfen Devran Durmaz ile iletişime geçin:

[devranaktas153@gmail.com]
