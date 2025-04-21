"""formulasa.py"""
import numpy as np
from scipy.integrate import solve_ivp
from typing import Dict, Any
import json

def termal_skoru_degisimi(t, ts, ns, parametreler):
    nabla2_ts = 0.0  # Basitleştirilmiş uzaysal terim
    return parametreler["DT"] * nabla2_ts + parametreler["alpha"] * ts * ns - parametreler["beta"] * ns

def basinc_skoru_degisimi(t, bs, ts, dp, parametreler):
    return parametreler["gamma"] * (dp + parametreler["lambda_"] * ts) - parametreler["delta"] * bs**2

def notron_skoru_degisimi(t, ns, ts, parametreler):
    return parametreler["epsilon"] + parametreler["phi"] - parametreler["zeta"] * ns * ts

def radyasyon_skoru_degisimi(t, rs, r_dose, parametreler):
    return parametreler["eta"] * r_dose - parametreler["theta"] * rs

def risk_degerlendirme(ts, bs, ns, rs, parametreler):
    f_ts = ts
    g_bs = bs
    h_ns = ns
    k_rs = rs
    return (parametreler["w_TS"] * f_ts + parametreler["w_BS"] * g_bs +
            parametreler["w_NS"] * h_ns + parametreler["w_RS"] * k_rs)

def hesapla_awora_flx(ham_veri: Dict[str, Any], parametreler: Dict[str, float], zaman_araligi: tuple = (0, 10), zaman_adim_sayisi: int = 100):
    """
    Ham veriyi alır ve Awora-FLX formüllerini kullanarak skorları ve risk değerini hesaplar.

    Args:
        ham_veri (Dict[str, Any]): Core'dan gelen ham veri.
        parametreler (Dict[str, float]): Diferansiyel denklem ve risk değerlendirme parametreleri.
        zaman_araligi (tuple): Simülasyonun zaman aralığı (başlangıç, bitiş).
        zaman_adim_sayisi (int): Simülasyon için kullanılacak zaman adımı sayısı.

    Returns:
        Dict[str, np.ndarray]: Zaman serisi için hesaplanmış skorlar (TS, BS, NS, RS) ve risk değeri (G).
    """
    t_span = zaman_araligi
    t_eval = np.linspace(t_span[0], t_span[1], zaman_adim_sayisi)

    initial_conditions = [
        ham_veri.get("TS", 1.0),
        ham_veri.get("BS", 1.0),
        ham_veri.get("NS", 1.0),
        ham_veri.get("RS", 1.0)
    ]

    def sistem(t, y):
        ts, bs, ns, rs = y
        dts_dt = termal_skoru_degisimi(t, ts, ham_veri.get("NS", 1.0), parametreler) # Anlık NS kullanımı
        dbs_dt = basinc_skoru_degisimi(t, bs, ts, ham_veri.get("dP", 0.0), parametreler)
        dns_dt = notron_skoru_degisimi(t, ns, ts, parametreler)
        drs_dt = radyasyon_skoru_degisimi(t, rs, ham_veri.get("Radyasyon_Dozu", 0.0), parametreler)
        return [dts_dt, dbs_dt, dns_dt, drs_dt]

    sol = solve_ivp(sistem, t_span, initial_conditions, t_eval=t_eval, method='RK45')

    g_degerleri = risk_degerlendirme(sol.y[0], sol.y[1], sol.y[2], sol.y[3], parametreler)

    return {
        "zaman": sol.t.tolist(),
        "TS": sol.y[0].tolist(),
        "BS": sol.y[1].tolist(),
        "NS": sol.y[2].tolist(),
        "RS": sol.y[3].tolist(),
        "G": g_degerleri.tolist()
    }

if __name__ == "__main__":
    ornek_ham_veri = {"TS": 1.05, "BS": 1.1, "NS": 1.02, "RS": 0.95, "dP": 0.01, "Radyasyon_Dozu": 0.001}
    ornek_parametreler = {
        "DT": 0.01, "alpha": 0.001, "beta": 0.1, "gamma": 0.05, "lambda_": 0.2, "delta": 0.02,
        "epsilon": 1e-6, "phi": 1e-5, "zeta": 0.0005, "eta": 0.01, "theta": 0.005,
        "w_TS": 0.25, "w_BS": 0.25, "w_NS": 0.25, "w_RS": 0.25
    }
    sonuclar = hesapla_awora_flx(ornek_ham_veri, ornek_parametreler)
    print(json.dumps(sonuclar, indent=4))