"""
AWORA-REACTOR-CS
================

Bu program, Awora-FLX çekirdeği ve bileşenleriyle verilen ham veriler ve yapılandırma dosyası üzerinden çeşitli skorlar (TS, BS, NS, RS) ve risk değeri (G) hesaplar. Hesaplamalar fiziksel ve matematiksel modellere dayalıdır.

KULLANIM KILAVUZU
-----------------
1. `config.json` ve ham veri dosyanızı (ör: `input.json`) hazırlayın.
2. Terminalde:
   python awora_reactor.py --config config.json --data input.json --output sonuc.json
3. Sonuçlar, belirttiğiniz JSON dosyasına kaydedilecektir.

Komut satırı argümanları:
  --config   : Yapılandırma dosyası yolu
  --data     : Ham veri dosyası yolu
  --output   : Sonuçların yazılacağı dosya yolu

"""
import json
import logging
import argparse
import platform
import uuid
import numpy as np
from scipy.integrate import solve_ivp
from typing import Dict, Any, List

# --- Yardımcı Fonksiyonlar (Sistem Bilgisi ve Loglama) ---
import sys
LOG_FILE = "awora_reactor.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
class MultiLogger:
    def __init__(self, log_file=LOG_FILE):
        self.logger = logging.getLogger("awora_logger")
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(LOG_FORMAT)
        # File handler
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        # Add handlers if not already
        if not self.logger.handlers:
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)
    def info(self, msg):
        self.logger.info(msg)
    def warning(self, msg):
        self.logger.warning(msg)
    def error(self, msg):
        self.logger.error(msg)

multi_logger = MultiLogger()

def bilgi_mesaji(mesaj):
    logging.info(mesaj)
    print(f"[BİLGİ] {mesaj}")

def bilgi_mesaji(mesaj, ekrana_yaz=True):
    multi_logger.info(mesaj)
    if ekrana_yaz:
        print(f"[BİLGİ] {mesaj}")

def uyari_mesaji(mesaj, ekrana_yaz=True):
    multi_logger.warning(mesaj)
    if ekrana_yaz:
        print(f"[UYARI] {mesaj}")

def hata_mesaji(mesaj, ekrana_yaz=True):
    multi_logger.error(mesaj)
    if ekrana_yaz:
        print(f"[HATA] {mesaj}")

def uyari_mesaji(mesaj):
    logging.warning(mesaj)
    print(f"[UYARI] {mesaj}")

def hata_mesaji(mesaj):
    logging.error(mesaj)
    print(f"[HATA] {mesaj}")

def get_system_info():
    return {
        "platform": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "uuid": str(uuid.uuid1())
    }

# --- Veri Okuma ---
def read_json(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        hata_mesaji(f"Dosya bulunamadı: {file_path}")
        raise
    except json.JSONDecodeError:
        hata_mesaji(f"Geçersiz JSON formatı: {file_path}")
        raise
    except Exception as e:
        hata_mesaji(f"Dosya okunurken beklenmeyen hata: {e}")
        raise

# --- Awora-FLX Formülleri ---
def termal_skoru_degisimi(t, ts, ns, parametreler):
    nabla2_ts = 0.0
    return parametreler["DT"] * nabla2_ts + parametreler["alpha"] * ts * ns - parametreler["beta"] * ns

def basinc_skoru_degisimi(t, bs, ts, dp, parametreler):
    return parametreler["gamma"] * (dp + parametreler["lambda_"] * ts) - parametreler["delta"] * bs**2

def notron_skoru_degisimi(t, ns, ts, parametreler):
    return parametreler["epsilon"] + parametreler["phi"] - parametreler["zeta"] * ns * ts

def radyasyon_skoru_degisimi(t, rs, r_dose, parametreler):
    return parametreler["eta"] * r_dose - parametreler["theta"] * rs

def risk_degerlendirme(ts, bs, ns, rs, parametreler):
    return (parametreler["w_TS"] * ts +
            parametreler["w_BS"] * bs +
            parametreler["w_NS"] * ns +
            parametreler["w_RS"] * rs)


def hesapla_awora_flx(ham_veri: Dict[str, Any], parametreler: Dict[str, float], zaman_araligi: tuple = (0, 10), zaman_adim_sayisi: int = 100, aşamalı_log: bool = False, aşama_log_dosyası: str = None):
    t_span = zaman_araligi
    t_eval = np.linspace(t_span[0], t_span[1], zaman_adim_sayisi)
    initial_conditions = [
        ham_veri.get("TS", 1.0),
        ham_veri.get("BS", 1.0),
        ham_veri.get("NS", 1.0),
        ham_veri.get("RS", 1.0)
    ]
    aşama_log = []
    def sistem(t, y):
        ts, bs, ns, rs = y
        dts_dt = termal_skoru_degisimi(t, ts, ham_veri.get("NS", 1.0), parametreler)
        dbs_dt = basinc_skoru_degisimi(t, bs, ts, ham_veri.get("dP", 0.0), parametreler)
        dns_dt = notron_skoru_degisimi(t, ns, ts, parametreler)
        drs_dt = radyasyon_skoru_degisimi(t, rs, ham_veri.get("Radyasyon_Dozu", 0.0), parametreler)
        if aşamalı_log:
            aşama = {
                "t": t,
                "TS": ts,
                "BS": bs,
                "NS": ns,
                "RS": rs,
                "dTS": dts_dt,
                "dBS": dbs_dt,
                "dNS": dns_dt,
                "dRS": drs_dt
            }
            multi_logger.info(f"AŞAMA | t={t:.4f} TS={ts:.4f} BS={bs:.4f} NS={ns:.4f} RS={rs:.4f} dTS={dts_dt:.4f} dBS={dbs_dt:.4f} dNS={dns_dt:.4f} dRS={drs_dt:.4f}")
            aşama_log.append(aşama)
        return [dts_dt, dbs_dt, dns_dt, drs_dt]
    sonuc = solve_ivp(sistem, t_span, initial_conditions, t_eval=t_eval)
    ts, bs, ns, rs = sonuc.y
    g = [risk_degerlendirme(ts[i], bs[i], ns[i], rs[i], parametreler) for i in range(len(ts))]
    if aşamalı_log and aşama_log_dosyası:
        try:
            with open(aşama_log_dosyası, "w", encoding="utf-8") as f:
                json.dump(aşama_log, f, indent=4, ensure_ascii=False)
            multi_logger.info(f"Aşamalı log dosyası kaydedildi: {aşama_log_dosyası}")
        except Exception as e:
            multi_logger.error(f"Aşama log dosyası yazılamadı: {e}")
    return {
        "zaman": t_eval.tolist(),
        "TS": ts.tolist(),
        "BS": bs.tolist(),
        "NS": ns.tolist(),
        "RS": rs.tolist(),
        "G": g
    }

# --- Sonuç Düzenleme ve Yazma ---
class Calculator:
    def __init__(self, awora_flx_sonuclari: Dict[str, List[float]], ham_veri_konumu: str):
        self.awora_flx_sonuclari = awora_flx_sonuclari
        self.ham_veri_konumu = ham_veri_konumu
    def duzenle_cikti(self) -> Dict[str, Any]:
        cikti = {
            "ham_veri_konumu": self.ham_veri_konumu,
            "zaman_serisi": []
        }
        zaman = self.awora_flx_sonuclari.get("zaman", [])
        ts = self.awora_flx_sonuclari.get("TS", [])
        bs = self.awora_flx_sonuclari.get("BS", [])
        ns = self.awora_flx_sonuclari.get("NS", [])
        rs = self.awora_flx_sonuclari.get("RS", [])
        g = self.awora_flx_sonuclari.get("G", [])
        for i in range(len(zaman)):
            cikti["zaman_serisi"].append({
                "zaman": f"{zaman[i]:.2f}",
                "TS": f"{ts[i]:.4f}",
                "BS": f"{bs[i]:.4f}",
                "NS": f"{ns[i]:.4f}",
                "RS": f"{rs[i]:.4f}",
                "G": f"{g[i]:.4f}"
            })
        return cikti
    def write_output(self, output_file_path: str, ekrana_yaz: bool = False):
        try:
            cikti = self.duzenle_cikti()
            with open(output_file_path, "w") as f:
                json.dump(cikti, f, indent=4)
            bilgi_mesaji(f"Çıktı dosyası başarıyla oluşturuldu: {output_file_path}")
            if ekrana_yaz:
                print(json.dumps(cikti, indent=4, ensure_ascii=False))
        except Exception as e:
            hata_mesaji(f"Çıktı dosyası oluşturulurken hata oluştu: {e}")

# --- Ana Akış ---
def main():
    parser = argparse.ArgumentParser(description="Awora-Reactor-CS: Awora-FLX hesaplama ve analiz aracı.")
    parser.add_argument('--config', required=True, help='Yapılandırma dosyası (JSON)')
    parser.add_argument('--data', required=True, help='Ham veri dosyası (JSON)')
    parser.add_argument('--output', required=True, help='Çıktı dosyası (JSON)')
    parser.add_argument('--print', action='store_true', help='Çıktıyı ekrana da yazdır')
    parser.add_argument('--step-log', help='Aşamalı log dosyası (opsiyonel)')
    args = parser.parse_args()
    bilgi_mesaji("Awora-Reactor-CS başlatıldı.")
    bilgi_mesaji(f"Sistem Bilgisi: {get_system_info()}")
    try:
        config = read_json(args.config)
        raw_data = read_json(args.data)
    except Exception:
        hata_mesaji("Gerekli dosyalar yüklenemedi. Çıkılıyor.")
        return
    parametreler = config.get("awora_flx_parametreleri", {
        "DT": 0.01, "alpha": 0.001, "beta": 0.1, "gamma": 0.05, "lambda_": 0.2, "delta": 0.02,
        "epsilon": 1e-6, "phi": 1e-5, "zeta": 0.0005, "eta": 0.01, "theta": 0.005,
        "w_TS": 0.25, "w_BS": 0.25, "w_NS": 0.25, "w_RS": 0.25
    })
    zaman_araligi = config.get("simulasyon_ayarlari", {}).get("zaman_araligi", (0, 10))
    zaman_adim_sayisi = config.get("simulasyon_ayarlari", {}).get("zaman_adim_sayisi", 100)
    try:
        awora_flx_sonuclari = hesapla_awora_flx(
            raw_data, parametreler, zaman_araligi, zaman_adim_sayisi,
            aşamalı_log=bool(args.step_log), aşama_log_dosyası=args.step_log
        )
        calc = Calculator(awora_flx_sonuclari, args.data)
        calc.write_output(args.output, ekrana_yaz=args.print)
        bilgi_mesaji("Awora-Reactor-CS başarıyla tamamlandı.")
    except Exception as e:
        hata_mesaji(f"Hesaplama sırasında hata oluştu: {e}")

# --- Basit Test Fonksiyonu ---
def test_awora_reactor():
    """Basit birim test: örnek veriyle hesaplama ve çıktı kontrolü."""
    test_config = {
        "awora_flx_parametreleri": {
            "DT": 0.01, "alpha": 0.001, "beta": 0.1, "gamma": 0.05, "lambda_": 0.2, "delta": 0.02,
            "epsilon": 1e-6, "phi": 1e-5, "zeta": 0.0005, "eta": 0.01, "theta": 0.005,
            "w_TS": 0.25, "w_BS": 0.25, "w_NS": 0.25, "w_RS": 0.25
        },
        "simulasyon_ayarlari": {
            "zaman_araligi": (0, 1),
            "zaman_adim_sayisi": 5
        }
    }
    test_data = {
        "TS": 1.0,
        "BS": 1.0,
        "NS": 1.0,
        "RS": 1.0,
        "dP": 0.0,
        "Radyasyon_Dozu": 0.0
    }
    try:
        sonuc = hesapla_awora_flx(test_data, test_config["awora_flx_parametreleri"],
                                  test_config["simulasyon_ayarlari"]["zaman_araligi"],
                                  test_config["simulasyon_ayarlari"]["zaman_adim_sayisi"])
        calc = Calculator(sonuc, "test_data.json")
        cikti = calc.duzenle_cikti()
        assert "zaman_serisi" in cikti
        assert len(cikti["zaman_serisi"]) == 5
        print("[TEST] Basit test başarıyla geçti.")
    except Exception as e:
        print(f"[TEST] Test başarısız: {e}")

if __name__ == "__main__":
    import sys
    if "test" in sys.argv:
        test_awora_reactor()
    else:
        main()
