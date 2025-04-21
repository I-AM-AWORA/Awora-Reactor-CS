"""
calculator.py

Awora-FLX hesaplamalarını yapan ve sonuçları düzenleyen sınıf.
"""

from typing import Dict, Any, List
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


class Calculator:
    def __init__(self, data: Dict[str, Any], data_source_path: str):
        """
        Calculator sınıfının başlatıcı metodu.

        Args:
            data: Girdi verilerini içeren sözlük.
            data_source_path: Veri dosyasının konumu.
        """
        self.data_source_path = data_source_path
        self.data = data
        self.results: Dict[str, Any] = {}  # Hesaplama sonuçları
        self.steps: List[str] = []  # Hesaplama adımları
        self.integrated_data: Dict[str, Any] = {}  # İntegral verileri
        self.categorized_results: Dict[str, str] = {}  # Kategorize edilmiş sonuçlar
        self.value_types: Dict[str, str] = {}  # Değer tipleri

    def _determine_value_type(self, value: Any) -> str:
        """
        Değerin tipini belirler.

        Args:
            value: Tipini belirlenecek değer.

        Returns:
            Değerin tipi ("float", "string", "list" veya "unknown").
        """
        if isinstance(value, (int, float)):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "list"
        else:
            return "unknown"

    def calculate_all(self):
        """
        Tüm hesaplamaları yapar ve sonuçları düzenler.
        """
        olculen = self.data.get("Olculen_Degerler", {})
        referans = self.data.get("Referans_Degerleri", {})

        # Skorları hesapla
        ts = calculate_ts(
            olculen.get("Sicaklik_Farki", 0.0),
            olculen.get("Isı_Akışı", 0.0),
            olculen.get("Sıcaklık_Gradyanı", 0.0),
            referans.get("Sıcaklik_Farkı", 0.0),
            referans.get("Isı_Akışı", 0.0),
            referans.get("Sıcaklık_Gradyanı", 0.0),
        )
        self.results["TS"] = ts
        self.steps.append(f"TS Hesaplandı: {ts}")
        self.value_types["TS"] = self._determine_value_type(ts)

        bs = calculate_bs(
            olculen.get("Basinc_Farki", 0.0),
            olculen.get("Gerilim", 0.0),
            referans.get("Basinc_Farki", 0.0),
            referans.get("Gerilim", 0.0),
        )
        self.results["BS"] = bs
        self.steps.append(f"BS Hesaplandı: {bs}")
        self.value_types["BS"] = self._determine_value_type(bs)

        ns = calculate_ns(
            olculen.get("Notron_Akisi", 0.0),
            olculen.get("Fizyon_Zincir_Reaksiyonu", 0.0),
            referans.get("Notron_Akisi", 0.0),
            referans.get("Fizyon_Zincir_Reaksiyonu", 0.0),
        )
        self.results["NS"] = ns
        self.steps.append(f"NS Hesaplandı: {ns}")
        self.value_types["NS"] = self._determine_value_type(ns)

        rs = calculate_rs(
            olculen.get("Radyasyon_Dozu", 0.0),
            referans.get("Radyasyon_Dozu", 0.0),
            olculen.get("Pradiation", 0.0),
            referans.get("Pref", 0.0)
        )
        self.results["RS"] = rs
        self.steps.append(f"RS Hesaplandı: {rs}")
        self.value_types["RS"] = self._determine_value_type(rs)

        # Ana skor (G) hesaplaması (ağırlıklar varsayılan olarak verildi)
        g_prime = (
            0.4 * self.results.get("TS", 0.0)
            + 0.2 * self.results.get("NS", 0.0)
            + 0.2 * self.results.get("BS", 0.0)
            + 0.2 * self.results.get("RS", 0.0)
        )
        self.results["G"] = g_prime
        self.steps.append(f"G Hesaplandı: {g_prime}")
        self.value_types["G"] = self._determine_value_type(g_prime)

        # Diferansiyel denklemler (örnek olarak ilk değerlerle hesaplama)
        # NOT: Diferansiyel denklemlerin nasıl kullanılacağı belirsiz, bu yüzden basit bir örnek yapıldı
        dt = 1  # Zaman adımı (örnek)
        nabla2TS = 1 # örnek değer
        alpha = 1 # örnek değer
        beta = 1 # örnek değer
        gamma = 1 # örnek değer
        lambda_ = 1 # örnek değer
        delta = 1 # örnek değer
        epsilon = 1 # örnek değer
        phi = 1 # örnek değer
        zeta = 1 # örnek değer
        eta = 1 # örnek değer
        theta = 1 # örnek değer
        Rdose = 1 # örnek değer

        self.results["dTSdt"] = dts_dt(self.results.get("TS", 0.0), self.results.get("NS", 0.0), DT=dt, alpha=alpha, beta=beta, nabla2TS=nabla2TS)
        self.results["dBSdt"] = dbs_dt(self.results.get("BS", 0.0), self.results.get("TS", 0.0), deltaP=dt, gamma=gamma, lambda_=lambda_, delta=delta)
        self.results["dNSdt"] = dns_dt(self.results.get("NS", 0.0), self.results.get("TS", 0.0), epsilon=epsilon, phi=phi, zeta=zeta)
        self.results["dRSdt"] = drs_dt(self.results.get("RS", 0.0), Rdose=Rdose, eta=eta, theta=theta)

        self.steps.append("Diferansiyel denklemler hesaplandı (örnek değerlerle)")
        self.value_types["dTSdt"] = self._determine_value_type(self.results["dTSdt"])
        self.value_types["dBSdt"] = self._determine_value_type(self.results["dBSdt"])
        self.value_types["dNSdt"] = self._determine_value_type(self.results["dNSdt"])
        self.value_types["dRSdt"] = self._determine_value_type(self.results["dRSdt"])

        self._categorize_results()
        self._integrate_data()

    def _categorize_results(self):
        """
        Hesaplama sonuçlarını kategorilere ayırır (AS, I, M).
        """
        for key, value in self.results.items():
            if key == "G":  # Sadece G için kategorizasyon
                if value > 1.0:
                    self.categorized_results[key] = "AS"
                elif 0.5 < value <= 1.0:
                    self.categorized_results[key] = "I"
                else:
                    self.categorized_results[key] = "M"
                self.value_types[key] = self._determine_value_type(
                    self.categorized_results[key]
                )

    def _integrate_data(self):
        """
        İntegral hesaplamalarını yapar (örnek olarak ortalama).
        """
        if self.results:
            self.integrated_data["ortalama_skor"] = sum(self.results.values()) / len(
                self.results
            )
            self.value_types["ortalama_skor"] = self._determine_value_type(
                self.integrated_data["ortalama_skor"]
            )

    def get_results(self) -> Dict[str, Any]:
        """
        Hesaplama sonuçlarını, adımları, kategorize edilmiş sonuçları ve
        integral verilerini döndürür.

        Returns:
            Bir sözlük içinde hesaplama sonuçları.
        """
        return {
            "ham_veri_konumu": self.data_source_path,
            "hesaplamalar": self.steps,
            "sonuclar": self.results,
            "cikan_deger_tipleri": self.value_types,
            "kategorize_edilmis_sonuclar": self.categorized_results,
            "integral_ve_turetilmis_veriler": self.integrated_data,
        }

    def write_output(self, file_path: str):
        """
        Hesaplama sonuçlarını bir dosyaya yazar (JSON formatında).

        Args:
            file_path: Çıktı dosyasının yolu.
        """
        import json

        with open(file_path, "w") as f:
            json.dump(self.get_results(), f, indent=4)