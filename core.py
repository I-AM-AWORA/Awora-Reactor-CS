# -- AWORA-FLX CORE ID: 100
# -- AWORA-FLX CORE Version: 1.0.0

import json
import logging
from typing import Dict, Any
from formulasa import hesapla_awora_flx

def load_config(config_path: str) -> Dict[str, Any]:
    """Yapılandırma dosyasını yükler."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Yapılandırma dosyası bulunamadı: {config_path}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Yapılandırma dosyası geçersiz JSON formatında: {config_path}")
        return {}

def load_raw_data(data_path: str) -> Dict[str, Any]:
    """Ham veri dosyasını yükler."""
    try:
        with open(data_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Ham veri dosyası bulunamadı: {data_path}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Ham veri dosyası geçersiz JSON formatında: {data_path}")
        return {}

def process_data(raw_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Ham veriyi işler ve Awora-FLX sonuçlarını hesaplar."""
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

    awora_flx_sonuclari = hesapla_awora_flx(raw_data, parametreler, zaman_araligi, zaman_adim_sayisi)
    return awora_flx_sonuclari

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config_path = "config.json"
    data_path = "input.json"

    config = load_config(config_path)
    raw_data = load_raw_data(data_path)

    if raw_data and config:
        awora_flx_output = process_data(raw_data, config)
        print(json.dumps(awora_flx_output, indent=4))