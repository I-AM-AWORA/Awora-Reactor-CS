#!/usr/bin/env python3
# -- AWORA-FLX CORE ID: 103 (Örn. Daha da gelişmiş bir ID)
# -- AWORA-FLX CORE Version: 3.0.1 (Örn. Büyük bir revizyon)

import json
import logging
from typing import Dict, Any, List, Tuple
import numpy as np
from scipy.signal import savgol_filter  # Diferansiyel için örnek filtre
from sklearn.linear_model import LinearRegression  # Temel tahmin için
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow import keras  # Daha gelişmiş tahmin modelleri için (LSTM)
import matplotlib.pyplot as plt  # Görselleştirme (örnek amaçlı)
import pandas as pd  # DataFrame işlemleri için

# Awora-FLX'e özgü terimler için sabitler
AWORA_SKALER = "awora_skaler"
AWORA_VEKTOR = "awora_vektor"
AWORA_TENSOR = "awora_tensor"
AWORA_GULAYA = "awora_gulaya"  # G değeri
AWORA_AD = "awora_ad"  # AS değer
AWORA_NAD = "awora_nad"  # NAD değeri
# ... diğer Awora-FLX terimleri

def load_config(config_path: str) -> Dict[str, Any]:
    """Awora-FLX yapılandırma dosyasını yükler."""

    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Yapılandırma dosyası bulunamadı: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Yapılandırma dosyası geçersiz JSON formatında: {config_path} - Hata: {e}")
        return {}
    except IOError as e:
        logging.error(f"Yapılandırma dosyası okuma hatası: {config_path} - Hata: {e}")
        return {}

def load_raw_data(data_path: str) -> Dict[str, Any]:
    """Awora-FLX ham veri dosyasını yükler."""

    try:
        with open(data_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Ham veri dosyası bulunamadı: {data_path}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Ham veri dosyası geçersiz JSON formatında: {data_path} - Hata: {e}")
        return {}
    except IOError as e:
        logging.error(f"Ham veri dosyası okuma hatası: {data_path} - Hata: {e}")
        return {}

def hesapla_diferansiyel_awora(veri: np.ndarray, adim: int = 1, yontem: str = "merkez", filtre_penceresi: int = 5,
                            filtre_polinomu: int = 2) -> np.ndarray:
    """Awora-FLX için özelleştirilmiş diferansiyel hesaplar."""

    if veri.ndim == 1:
        if yontem == "ileri":
            return np.diff(veri, n=adim) / adim
        elif yontem == "geri":
            return (veri[adim:] - veri[:-adim]) / adim
        elif yontem == "merkez":
            if adim > 0:
                pad_genisligi = adim
                padded_veri = np.pad(veri, (pad_genisligi, pad_genisligi), mode='edge')
                return (padded_veri[2 * pad_genisligi:] - padded_veri[:len(veri)]) / (2 * adim)
            else:
                logging.warning("Diferansiyel adımı sıfırdan büyük olmalıdır.")
                return np.zeros_like(veri)
        elif yontem == "savgol":
            if filtre_penceresi >= 3 and filtre_penceresi % 2 == 1 and filtre_polinomu >= 0:
                return savgol_filter(veri, filtre_penceresi, filtre_polinomu, deriv=1, mode='nearest')
            else:
                logging.warning("Geçersiz Savitzky-Golay filtre parametreleri. Merkez yöntemi kullanılıyor.")
                return (np.roll(veri, -adim) - np.roll(veri, adim)) / (2 * adim)
        else:
            logging.warning(f"Diferansiyel yöntemi '{yontem}' tanınmıyor. Merkez kullanılıyor.")
            return (np.roll(veri, -adim) - np.roll(veri, adim)) / (2 * adim)
    else:
        logging.warning("Diferansiyel hesabı şu anda sadece 1 boyutlu (zamana bağlı) veriler için destekleniyor.")
        return np.zeros_like(veri)

def tahmin_et_awora(veri: np.ndarray, model_tipi: str, gecmis_adim_sayisi: int,
                    gelecek_adim_sayisi: int, model_parametreleri: Dict[str, Any] = {}) -> np.ndarray:
    """Awora-FLX için özelleştirilmiş tahmin yapar."""

    n_gecmis = len(veri)
    if n_gecmis < gecmis_adim_sayisi:
        logging.warning(f"Tahmin için yeterli geçmiş veri yok ({n_gecmis} < {gecmis_adim_sayisi}).")
        return np.array([])

    if model_tipi == "dogrusal_regresyon":
        gecmis_x = np.arange(n_gecmis).reshape(-1, 1)
        gecmis_y = veri.reshape(-1, 1)
        model = LinearRegression(**model_parametreleri)
        model.fit(gecmis_x[-gecmis_adim_sayisi:], gecmis_y[-gecmis_adim_sayisi:])
        gelecek_x = np.arange(n_gecmis, n_gecmis + gelecek_adim_sayisi).reshape(-1, 1)
        tahminler = model.predict(gelecek_x).flatten()
        return tahminler

    elif model_tipi == "lstm":
        # Veriyi ölçekle
        scaler = StandardScaler()
        scaled_veri = scaler.fit_transform(veri.reshape(-1, 1))

        # Zaman serisi verisini uygun formata dönüştür
        X, y = [], []
        for i in range(gecmis_adim_sayisi, len(scaled_veri)):
            X.append(scaled_veri[i - gecmis_adim_sayisi:i, 0])
            y.append(scaled_veri[i, 0])
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))

        # LSTM modelini oluştur
        model = keras.Sequential()
        model.add(keras.layers.LSTM(units=model_parametreleri.get("lstm_units", 50),
                                   return_sequences=True,
                                   input_shape=(X.shape[1], 1)))
        model.add(keras.layers.LSTM(units=model_parametreleri.get("lstm_units", 50)))
        model.add(keras.layers.Dense(units=gelecek_adim_sayisi))  # Tahmin adımı kadar çıktı
        model.compile(optimizer=model_parametreleri.get("optimizer", 'adam'),
                      loss=model_parametreleri.get("loss", 'mean_squared_error'),
                      metrics=model_parametreleri.get("metrics", ['mae']))

        # Eğitim etiketlerini yeniden şekillendir
        y = np.tile(y.reshape(-1, 1), (1, gelecek_adim_sayisi))  # y'yi (batch_size, gelecek_adim_sayisi) yap
        
        # Modeli eğit
        model.fit(X, y, epochs=model_parametreleri.get("epochs", 10),
                  batch_size=model_parametreleri.get("batch_size", 32), verbose=0)

        # Tahmin yap
        son_gecmis = scaled_veri[-gecmis_adim_sayisi:].reshape(1, gecmis_adim_sayisi, 1)
        tahminler_scaled = model.predict(son_gecmis, verbose=0)
        tahminler = scaler.inverse_transform(tahminler_scaled).flatten()
        return tahminler

    # Buraya diğer Awora-FLX'e özgü tahmin modelleri eklenebilir.
    else:
        logging.warning(f"Tahmin modeli '{model_tipi}' tanınmıyor. Doğrusal regresyon kullanılıyor.")
        gecmis_x = np.arange(n_gecmis).reshape(-1, 1)
        gecmis_y = veri.reshape(-1, 1)
        model = LinearRegression()
        model.fit(gecmis_x[-gecmis_adim_sayisi:], gecmis_y[-gecmis_adim_sayisi:])
        gelecek_x = np.arange(n_gecmis, n_gecmis + gelecek_adim_sayisi).reshape(-1, 1)
        tahminler = model.predict(gelecek_x).flatten()
        return tahminler
    

def hesapla_awora_flx(veri: Dict[str, np.ndarray], config: Dict[str, Any]) -> Dict[str, Any]:
    """Temel Awora-FLX hesaplamalarını yapar (örneğin, skorları hesaplar)."""

    sonuclar = {}

    # 1. Ham Skor Değerleri
    sonuclar["ts"] = veri["termal_skor"]
    sonuclar["bs"] = veri["basinc_skoru"]
    sonuclar["ns"] = veri["notron_skoru"]
    sonuclar["rs"] = veri["radyasyon_skoru"]

    # 2. Normalize Edilmiş Skorlar (Örnek Normalizasyon)
    referans_ts = config.get("referans_degerler", {}).get("termal_skor", 300)  #
    referans_bs = config.get("referans_degerler", {}).get("basinc_skoru", 15)  #
    referans_ns = config.get("referans_degerler", {}).get("notron_skoru", 1e13)  #
    referans_rs = config.get("referans_degerler", {}).get("radyasyon_skoru", 0.2)  #

    sonuclar["ts_norm"] = veri["termal_skor"] / referans_ts
    sonuclar["bs_norm"] = veri["basinc_skoru"] / referans_bs
    sonuclar["ns_norm"] = veri["notron_skoru"] / referans_ns
    sonuclar["rs_norm"] = veri["radyasyon_skoru"] / referans_rs

    # 3. Skorların Zamansal Değişim Hızları (Diferansiyeller)
    adim = config.get("diferansiyel_ayarlari", {}).get("adim", 1)
    yontem = config.get("diferansiyel_ayarlari", {}).get("yontem", "merkez")
    filtre_penceresi = config.get("diferansiyel_ayarlari", {}).get("filtre_penceresi", 5)
    filtre_polinomu = config.get("diferansiyel_ayarlari", {}).get("filtre_polinomu", 2)

    sonuclar["dts_dt"] = hesapla_diferansiyel_awora(veri["termal_skor"], adim, yontem, filtre_penceresi, filtre_polinomu)
    sonuclar["dbs_dt"] = hesapla_diferansiyel_awora(veri["basinc_skoru"], adim, yontem, filtre_penceresi, filtre_polinomu)
    sonuclar["dns_dt"] = hesapla_diferansiyel_awora(veri["notron_skoru"], adim, yontem, filtre_penceresi, filtre_polinomu)
    sonuclar["drs_dt"] = hesapla_diferansiyel_awora(veri["radyasyon_skoru"], adim, yontem, filtre_penceresi, filtre_polinomu)

    # 4. Genel Risk Skoru (G)
    w_ts = config.get("agirliklar", {}).get("termal_skor", 0.25)  # Örnek ağırlıklar
    w_bs = config.get("agirliklar", {}).get("basinc_skoru", 0.25)
    w_ns = config.get("agirliklar", {}).get("notron_skoru", 0.25)
    w_rs = config.get("agirliklar", {}).get("radyasyon_skoru", 0.25)

    # Basit lineer fonksiyonlar (f, g, h, k) - İhtiyaca göre değiştirilebilir
    f_ts = veri["termal_skor"]
    g_bs = veri["basinc_skoru"]
    h_ns = veri["notron_skoru"]
    k_rs = veri["radyasyon_skoru"]

    sonuclar["g_skoru"] = w_ts * f_ts + w_bs * g_bs + w_ns * h_ns + w_rs * k_rs

    # 5. İstatistiksel Değerler (Örnekler)
    sonuclar["ts_ortalama"] = np.mean(veri["termal_skor"])
    sonuclar["ts_standart_sapma"] = np.std(veri["termal_skor"])
    sonuclar["bs_max"] = np.max(veri["basinc_skoru"])
    sonuclar["rs_min"] = np.min(veri["radyasyon_skoru"])

    # 6. Zaman Serisi Verileri (Sadece referans için zamanı sakla)
    sonuclar["zaman"] = veri["zaman"].tolist()

    # 10. Skorlar Arası Korelasyonlar
    data_frame = pd.DataFrame({
        "ts": veri["termal_skor"],
        "bs": veri["basinc_skoru"],
        "ns": veri["notron_skoru"],
        "rs": veri["radyasyon_skoru"]
    })
    kor_matrisi = data_frame.corr()
    sonuclar["kor_matrisi"] = kor_matrisi.to_dict()

    return sonuclar

def uret_ornek_veri(zaman_adim_sayisi: int) -> Dict[str, np.ndarray]:
    """Örnek veri üretir (gerçek veri yerine)."""

    zaman = np.linspace(0, 10, zaman_adim_sayisi)  # Örnek zaman aralığı

    # Temel skorlar (örnek sinüs dalgaları + gürültü)
    termal_skor = 200 + 50 * np.sin(zaman) + 10 * np.random.randn(zaman_adim_sayisi)
    basinc_skoru = 10 + 2 * zaman + 0.5 * np.random.randn(zaman_adim_sayisi)
    notron_skoru = 1e13 + 1e12 * np.cos(2 * zaman) + 1e11 * np.random.randn(zaman_adim_sayisi)
    radyasyon_skoru = 0.1 + 0.05 * zaman + 0.01 * np.random.randn(zaman_adim_sayisi)

    veri = {
        "zaman": zaman,
        "termal_skor": termal_skor,
        "basinc_skoru": basinc_skoru,
        "notron_skoru": notron_skoru,
        "radyasyon_skoru": radyasyon_skoru
    }
    return veri

def process_data(raw_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Awora-FLX verilerini işler, diferansiyel alır ve tahmin yapar."""

    if not isinstance(raw_data, dict) or "veri" not in raw_data:
        logging.error("Geçersiz ham veri formatı.")
        return {}

    analiz_ayarlari = raw_data.get("analiz_ayarlari", {})
    diferansiyel_ayarlari = raw_data.get("diferansiyel_ayarlari", {})
    tahmin_ayarlari = raw_data.get("tahmin_ayarlari", {})
    sonuclar = {}

    for veri_adi, veri_degeri in raw_data["veri"].items():  # Değişiklik burada
        # Varsayalım ki her veri_degeri bir numpy array'dir. Eğer değilse, tip kontrolü eklemelisiniz.
        degerler = veri_degeri 

        veri_sonuclari = {}
        if analiz_ayarlari.get(f"{veri_adi}_ortalama", False):
            veri_sonuclari["ortalama"] = np.mean(degerler)
        if analiz_ayarlari.get(f"{veri_adi}_diferansiyel", False):
            adim = diferansiyel_ayarlari.get("adim", 1)
            yontem = diferansiyel_ayarlari.get("yontem", "merkez")
            filtre_penceresi = diferansiyel_ayarlari.get("filtre_penceresi", 5)
            filtre_polinomu = diferansiyel_ayarlari.get("filtre_polinomu", 2)
            veri_sonuclari["diferansiyel"] = hesapla_diferansiyel_awora(degerler, adim, yontem, filtre_penceresi,
                                                                      filtre_polinomu).tolist()
        if tahmin_ayarlari and tahmin_ayarlari.get(f"{veri_adi}_tahmin", False):
            model_tipi = tahmin_ayarlari.get("model", "dogrusal_regresyon")
            gecmis_adim_sayisi = tahmin_ayarlari.get("gecmis_adim_sayisi", 5)
            gelecek_adim_sayisi = tahmin_ayarlari.get("gelecek_adim_sayisi", 3)
            model_parametreleri = tahmin_ayarlari.get("model_parametreleri", {})
            tahminler = tahmin_et_awora(degerler, model_tipi, gecmis_adim_sayisi, gelecek_adim_sayisi,
                                      model_parametreleri).tolist()
            if tahminler:
                veri_sonuclari["tahmin"] = tahminler

        if veri_sonuclari:
            sonuclar[veri_adi] = veri_sonuclari

    return sonuclar

def ana_fonksiyon(config: Dict[str, Any], veri: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """Ana fonksiyon: Tüm Awora-FLX işlemlerini yönetir."""

    awora_sonuclari = hesapla_awora_flx(veri, config)
    islenmis_veri = process_data({"veri": veri}, config)  # process_data'ya uygun format
    # Tahminler
    tahminler = {}
    tahmin_ayarlari = config.get("tahmin_ayarlari", {})
    if tahmin_ayarlari:
        gecmis_adim_sayisi = tahmin_ayarlari.get("gecmis_adim_sayisi", 5)
        gelecek_adim_sayisi = tahmin_ayarlari.get("gelecek_adim_sayisi", 3)
        model_tipi = tahmin_ayarlari.get("model", "lstm")
        model_parametreleri = tahmin_ayarlari.get("model_parametreleri", {})
        for skor_adi in ["termal_skor", "basinc_skoru", "notron_skoru", "radyasyon_skoru"]:
            if skor_adi in veri:
                tahminler[skor_adi] = tahmin_et_awora(veri[skor_adi], model_tipi, gecmis_adim_sayisi,
                                                    gelecek_adim_sayisi, model_parametreleri).tolist()

    sonuclar = {
        "awora_flx": {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in awora_sonuclari.items()},
        "islenmis_veri": {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in islenmis_veri.items()},
        "tahminler": tahminler
    }

    return sonuclar
def main():
    """Ana fonksiyon."""

    config = load_config("config.json")  # Yapılandırma dosyasını yükle
    if not config:
        print("Yapılandırma yüklenemedi, varsayılan değerler kullanılıyor.")
        config = {}  # Varsayılan yapılandırma (gerekirse)

    zaman_adim_sayisi = config.get("zaman_adim_sayisi", 100)  # Yapılandırmadan veya varsayılan
    veri = uret_ornek_veri(zaman_adim_sayisi)
    sonuclar = ana_fonksiyon(config, veri)

    # Görselleştirme (örnek)
    if veri["zaman"].size > 0:
        plt.figure(figsize=(12, 6))
        plt.plot(veri["zaman"], veri["termal_skor"], label="Termal Skor (TS)")
        if "termal_skor" in sonuclar["tahminler"]:
            plt.plot(veri["zaman"][-len(sonuclar["tahminler"]["termal_skor"]):],
                     sonuclar["tahminler"]["termal_skor"], label="TS Tahmini", linestyle="--")
        plt.xlabel("Zaman")
        plt.ylabel("TS Değeri")
        plt.legend()
        plt.title("Termal Skor ve Tahmini")
        plt.grid(True)
        plt.show()
    else:
        print("Görselleştirme için yeterli veri yok.")

    # Sonuçları yazdır (veya dosyaya kaydet)
    print(json.dumps(sonuclar, indent=4))

if __name__ == "__main__":
    main()