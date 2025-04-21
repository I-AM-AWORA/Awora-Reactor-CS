# -- AWORA-FLX CORE ID: 100
# -- AWORA-FLX CORE Version: 1.0.0

import json
import logging
from typing import Dict, Any
from formulasa import hesapla_awora_flx
import cProfile
import pstats
import numpy as np
from numba import jit
import time

def load_config(config_path: str) -> Dict[str, Any]:
    """Yapılandırma dosyasını yükler."""
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
    """Ham veri dosyasını yükler."""
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

def process_data(raw_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Ham veriyi işler ve Awora-FLX sonuçlarını hesaplar."""
    if not isinstance(raw_data, dict):
        logging.error("Ham veri geçerli bir sözlük formatında değil.")
        return {}
    if not isinstance(config, dict):
        logging.error("Yapılandırma geçerli bir sözlük formatında değil.")
        return {}

    parametreler = config.get("awora_flx_parametreleri", {})
    zaman_araligi = config.get("simulasyon_ayarlari", {}).get("zaman_araligi", (0, 10))
    zaman_adim_sayisi = config.get("simulasyon_ayarlari", {}).get("zaman_adim_sayisi", 100)

    if not parametreler:
        logging.warning("Awora-FLX parametreleri yapılandırma dosyasında bulunamadı. Varsayılan değerler kullanılacak.")
        parametreler = {
            "DT": 0.01, "alpha": 0.001, "beta": 0.1, "gamma": 0.05, "lambda_": 0.2, "delta": 0.02,
            "epsilon": 1e-6, "phi": 1e-5, "zeta": 0.0005, "eta": 0.01, "theta": 0.005,
            "w_TS": 0.25, "w_BS": 0.25, "w_NS": 0.25, "w_RS": 0.25
        }

    # Basit veri validasyonu (geliştirilebilir)
    if "sensor_verileri" not in raw_data or not isinstance(raw_data["sensor_verileri"], list):
        logging.error("Ham veride 'sensor_verileri' bulunamadı veya geçerli bir liste değil.")
        return {}

    awora_flx_sonuclari = hesapla_awora_flx(raw_data["sensor_verileri"], parametreler, zaman_araligi, zaman_adim_sayisi)
    return {"awora_flx_sonuclari": awora_flx_sonuclari, "isleme_zamani": time.time()} # İzleme için zaman bilgisi eklendi

def run_profiler():
    profiler = cProfile.Profile()
    profiler.enable()
    return profiler

def print_profiler_stats(profiler):
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('tottime')
    stats.print_stats()

def health_check(son_isleme_zamani):
    """Basit bir sağlık kontrolü."""
    if son_isleme_zamani is None:
        return "Çekirdek henüz çalıştırılmadı."
    gecen_sure = time.time() - son_isleme_zamani
    if gecen_sure > 60:  # Son çalıştırmadan bu yana 60 saniyeden fazla geçtiyse sağlıksız kabul et
        return f"UYARI: Çekirdek en son {gecen_sure:.2f} saniye önce çalıştırıldı."
    else:
        return "Çekirdek sağlıklı çalışıyor."

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config_path = "config.json"
    data_path = "input.json"
    son_isleme_zamani = None

    # Performans Profilleme (isteğe bağlı, çalıştırmak için yorumu kaldırın)
    # profiler = run_profiler()

    config = load_config(config_path)
    raw_data = load_raw_data(data_path)

    if raw_data and config:
        awora_flx_output = process_data(raw_data, config)
        print(json.dumps(awora_flx_output, indent=4))
        son_isleme_zamani = awora_flx_output.get("isleme_zamani")

    # Performans Profilleme Sonuçları (isteğe bağlı, çalıştırmak için yorumu kaldırın)
    # if 'profiler' in locals():
    #     print("\n--- Performans Profilleme Sonuçları ---")
    #     print_profiler_stats(profiler)

    # Sağlık Kontrolü
    print("\n--- Çekirdek Sağlık Durumu ---")
    print(health_check(son_isleme_zamani))

    # Örnek Unit Test Senaryosu (basit bir örnek)
    print("\n--- Basit Unit Test Senaryosu ---")
    test_raw_data_basarili = {"sensor_verileri": [1, 2, 3]}
    test_config_basarili = {"awora_flx_parametreleri": {"DT": 0.01}, "simulasyon_ayarlari": {"zaman_araligi": [0, 1], "zaman_adim_sayisi": 10}}
    sonuc_basarili = process_data(test_raw_data_basarili, test_config_basarili)
    if "awora_flx_sonuclari" in sonuc_basarili:
        print("Test Başarılı: Temel işleme çalıştı.")
    else:
        print("Test Başarısız: Temel işleme hatası.")

    test_raw_data_hatali = {"yanlis_veri": [1, 2, 3]}
    sonuc_hatali = process_data(test_raw_data_hatali, test_config_basarili)
    if not sonuc_hatali:
        print("Test Başarılı: Hatalı ham veri doğru şekilde işlendi.")
    else:
        print("Test Başarısız: Hatalı ham veri işlenirken sorun oluştu.")