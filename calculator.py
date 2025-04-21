"""calculator.py"""
import json
import logging
from typing import Dict, Any, List

class Calculator:
    def __init__(self, awora_flx_sonuclari: Dict[str, List[float]], ham_veri_konumu: str):
        """
        Calculator sınıfının yapıcı metodu.

        Args:
            awora_flx_sonuclari (Dict[str, List[float]]): Core'dan gelen Awora-FLX sonuçları.
            ham_veri_konumu (str): Ham veri dosyasının konumu.
        """
        self.awora_flx_sonuclari = awora_flx_sonuclari
        self.ham_veri_konumu = ham_veri_konumu

    def duzenle_cikti(self) -> Dict[str, Any]:
        """
        Awora-FLX sonuçlarını düzenleyerek nihai çıktı formatına dönüştürür.
        """
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

    def write_output(self, output_file_path: str):
        """
        Çıktı verisini JSON dosyasına yazar.

        Args:
            output_file_path (str): Çıktı dosyasının konumu.
        """
        try:
            with open(output_file_path, "w") as f:
                json.dump(self.duzenle_cikti(), f, indent=4)
            logging.info(f"Çıktı dosyası başarıyla oluşturuldu: {output_file_path}")
        except Exception as e:
            logging.error(f"Çıktı dosyası oluşturulurken hata oluştu: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # Örnek Awora-FLX sonuçları (core.py'dan geldiğini varsayalım)
    ornek_awora_flx_sonuclari = {
        "zaman": [0.0, 0.1, 0.2, 0.3],
        "TS": [1.05, 1.055, 1.061, 1.068],
        "BS": [1.1, 1.105, 1.111, 1.118],
        "NS": [1.02, 1.021, 1.022, 1.023],
        "RS": [0.95, 0.951, 0.952, 0.953],
        "G": [1.01, 1.012, 1.014, 1.016]
    }
    input_file_path = "input.json"
    calculator = Calculator(ornek_awora_flx_sonuclari, input_file_path)
    cikti = calculator.duzenle_cikti()
    print(json.dumps(cikti, indent=4))
    calculator.write_output("output.json")