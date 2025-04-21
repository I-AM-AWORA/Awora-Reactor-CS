"""
core.py (Gelişmiş - Hız Odaklı)

Awora-FLX hesaplamalarını yapar ve ham sonuçları üretir (NumPy ve Numba ile hızlandırılmış).
"""

import json
from typing import Dict, Any, List
import logging
import numpy as np
from numba import jit

from data_reader import read_data
from formulas import (
    calculate_ts,
    calculate_bs,
    calculate_ns,
    calculate_rs,
    calculate_anh,
    dts_dt,
    dbs_dt,
    dns_dt,
    drs_dt,
)  # Formülleri içe aktar
from calculator import Calculator  # Calculator'ı içe aktar


class CalculationError(Exception):
    """Hesaplama sırasında oluşan hatalar için özel istisna sınıfı."""

    def __init__(self, message: str):
        super().__init__(message)


def read_input_data(file_path: str) -> Dict[str, Any]:
    """Girdi verilerini okur ve doğrular."""
    try:
        with open(file_path, "r") as f:
            raw_data = json.load(f)
        # Veri doğrulama işlemleri (gerekirse)
        # jsonschema.validate(instance=raw_data, schema=schema)
        return raw_data
    except FileNotFoundError as e:
        logging.error(f"Veri dosyası bulunamadı: {e}")
        raise  # İstisnayı yeniden yükselt
    except json.JSONDecodeError as e:
        logging.error(f"Geçersiz JSON: {e}")
        raise
    except Exception as e:
        logging.error(f"Veri okuma hatası: {e}")
        raise


@jit(nopython=True)
def calculate_scores_fast(
    olculen_sicaklik_farki,
    olculen_isi_akisi,
    olculen_sicaklik_gradyani,
    referans_sicaklik_farki,
    referans_isi_akisi,
    referans_sicaklik_gradyani,
    olculen_basinc_farki,
    olculen_gerilim,
    referans_basinc_farki,
    referans_gerilim,
    olculen_notron_akisi,
    olculen_fizyon_zincir_reaksiyonu,
    referans_notron_akisi,
    referans_fizyon_zincir_reaksiyonu,
    olculen_radyasyon_dozu,
    referans_radyasyon_dozu,
    olculen_Pradiation,
    referans_Pref,
):
    """Skorları hesaplar (Numba ile hızlandırılmış)."""

    ts = 0.0
    if referans_sicaklik_farki != 0.0:
        ts += olculen_sicaklik_farki / referans_sicaklik_farki
    if referans_isi_akisi != 0.0:
        ts += olculen_isi_akisi / referans_isi_akisi
    if referans_sicaklik_gradyani != 0.0:
        ts += olculen_sicaklik_gradyani / referans_sicaklik_gradyani

    bs = 0.0
    if referans_basinc_farki != 0.0:
        bs += olculen_basinc_farki / referans_basinc_farki
    if referans_gerilim != 0.0:
        bs += olculen_gerilim / referans_gerilim

    ns = 0.0
    if referans_notron_akisi != 0.0:
        ns += olculen_notron_akisi / referans_notron_akisi
    if referans_fizyon_zincir_reaksiyonu != 0.0:
        ns += olculen_fizyon_zincir_reaksiyonu / referans_fizyon_zincir_reaksiyonu

    rs = 0.0
    if referans_radyasyon_dozu != 0.0:
        rs += olculen_radyasyon_dozu / referans_radyasyon_dozu
    if referans_Pref != 0.0:
        rs += olculen_Pradiation / referans_Pref

    return ts, bs, ns, rs


def calculate_scores(data: Dict[str, Any]) -> Dict[str, float]:
    """Skorları hesaplar."""

    olculen = data.get("Olculen_Degerler", {})
    referans = data.get("Referans_Degerleri", {})

    try:
        (
            ts,
            bs,
            ns,
            rs,
        ) = calculate_scores_fast(  # Numba hızlandırması
            olculen.get("Sicaklik_Farki", 0.0),
            olculen.get("Isı_Akışı", 0.0),
            olculen.get("Sıcaklık_Gradyanı", 0.0),
            referans.get("Sicaklik_Farki", 0.0),
            referans.get("Isı_Akışı", 0.0),
            referans.get("Sıcaklık_Gradyanı", 0.0),
            olculen.get("Basinc_Farki", 0.0),
            olculen.get("Gerilim", 0.0),
            referans.get("Basinc_Farki", 0.0),
            referans.get("Gerilim", 0.0),
            olculen.get("Notron_Akisi", 0.0),
            olculen.get("Fizyon_Zincir_Reaksiyonu", 0.0),
            referans.get("Notron_Akisi", 0.0),
            referans.get("Fizyon_Zincir_Reaksiyonu", 0.0),
            olculen.get("Radyasyon_Dozu", 0.0),
            referans.get("Radyasyon_Dozu", 0.0),
            olculen.get("Pradiation", 0.0),
            referans.get("Pref", 0.0),
        )

        return {"TS": ts, "BS": bs, "NS": ns, "RS": rs}
    except Exception as e:
        logging.error(f"Skor hesaplama hatası: {e}")
        raise CalculationError("Skorlar hesaplanırken bir hata oluştu.") from e


def calculate_differential_equations(
    data: Dict[str, Any], scores: Dict[str, float]
) -> Dict[str, float]:
    """Diferansiyel denklemleri çözer."""

    diff_params = data.get("Diferansiyel_Denklem_Parametreleri", {})
    try:
        dt = diff_params.get("DT", 1.0)
        nabla2TS = diff_params.get("nabla2TS", 0.0)
        alpha = diff_params.get("alpha", 0.0)
        beta = diff_params.get("beta", 0.0)
        gamma = diff_params.get("gamma", 0.0)
        lambda_ = diff_params.get("lambda_", 0.0)
        delta = diff_params.get("delta", 0.0)
        epsilon = diff_params.get("epsilon", 0.0)
        phi = diff_params.get("phi", 0.0)
        zeta = diff_params.get("zeta", 0.0)
        eta = diff_params.get("eta", 0.0)
        theta = diff_params.get("theta", 0.0)
        Rdose_param = diff_params.get("Rdose", 0.0)

        dts_dt_value = dts_dt(
            scores["TS"], scores["NS"], DT=dt, alpha=alpha, beta=beta, nabla2TS=nabla2TS
        )
        dbs_dt_value = dbs_dt(
            scores["BS"], scores["TS"], deltaP=dt, gamma=gamma, lambda_=lambda_, delta=delta
        )
        dns_dt_value = dns_dt(
            scores["NS"], scores["TS"], epsilon=epsilon, phi=phi, zeta=zeta
        )
        drs_dt_value = drs_dt(
            scores["RS"], Rdose=Rdose_param, eta=eta, theta=theta
        )

        return {
            "dTSdt": dts_dt_value,
            "dBSdt": dbs_dt_value,
            "dNSdt": dns_dt_value,
            "dRSdt": drs_dt_value,
        }
    except Exception as e:
        logging.error(f"Diferansiyel denklem hatası: {e}")
        raise CalculationError(
            "Diferansiyel denklemler çözülürken hata oluştu."
        ) from e


def prepare_calculator_input(
    data: Dict[str, Any], scores: Dict[str, float], diff_results: Dict[str, float]
) -> Dict[str, Any]:
    """Calculator için girdi verisini hazırlar."""

    ham_sonuclar = {
        "ham_veri": data,
        **scores,
        **diff_results,
    }
    return ham_sonuclar


def main(input_file_path: str):
    logging.basicConfig(filename="awora.log", level=logging.INFO)
    try:
        raw_data = read_input_data(input_file_path)
        scores = calculate_scores(raw_data)
        diff_eq_results = calculate_differential_equations(raw_data, scores)
        calculator_input = prepare_calculator_input(
            raw_data, scores, diff_eq_results
        )

        calculator = Calculator(calculator_input, input_file_path)
        duzenlenmis_sonuclar = calculator.calculate_all()

        logging.info("Hesaplama başarıyla tamamlandı.")
        # ... Çıktı işlemleri ...
        print("Core.py'den çıkan ham sonuçlar:", calculator_input)
        print("Calculator'dan gelen düzenlenmiş sonuçlar:", duzenlenmis_sonuclar)
        calculator.write_output("output.json")

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        CalculationError,  # Buraya eklendi
    ) as e:
        print(f"Hata: {e}")
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")


if __name__ == "__main__":
    input_file = "input.json"
    main(input_file)