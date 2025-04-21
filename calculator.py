"""
calculator.py (Gelişmiş)

core.py'den gelen ham veriyi işleyerek nihai çıktıları düzenler.
"""

from typing import Dict, Any, List
import json
import logging

class Calculator:
    def __init__(self, ham_veri: Dict[str, Any], ham_veri_konumu: str):
        """
        Calculator sınıfının yapıcı metodu.

        Args:
            ham_veri (Dict[str, Any]): core.py'den gelen ham veri.
            ham_veri_konumu (str): Ham veri dosyasının konumu.
        """
        self.ham_veri = ham_veri
        self.ham_veri_konumu = ham_veri_konumu
        self.zaman_noktalari = self._veriyi_zamana_gore_ayristir()

    def _veriyi_zamana_gore_ayristir(self) -> Dict[str, Dict[str, Any]]:
        """
        Ham veriyi zamana göre ayrıştırır ve I, M, AS türlerini belirler.

        Returns:
            Dict[str, Dict[str, Any]]: Zamana göre ayrıştırılmış veri.
        """

        zaman_noktalari = {}
        # Bu kısım, ham verinin yapısına göre uyarlanmalıdır.
        # Şu an için örnek olarak, ham verinin bir zaman serisi
        # olduğunu ve her zaman noktası için skorları içerdiğini varsayıyoruz.
        # Gerçek uygulamada, verinin kaynağına ve formatına göre
        # bu kısmı düzenlemeniz gerekebilir.

        # Örnek: Eğer ham veri bir zaman serisi ise,
        # her zaman noktası için skorları ayıklayabiliriz.
        # Şimdilik, örnek bir veri yapısı oluşturalım:
        zaman_noktalari = {
            "d0": {  # Başlangıç zamanı
                "TS": {"deger": self.ham_veri.get("TS", 0.0)},
                "BS": {"deger": self.ham_veri.get("BS", 0.0)},
                "NS": {"deger": self.ham_veri.get("NS", 0.0)},
                "RS": {"deger": self.ham_veri.get("RS", 0.0)},
                "G": {"deger": self.ham_veri.get("G", 0.0)},
            },
            "d2": {  # 2 birim sonra
                "TS": {"deger": self.ham_veri.get("TS", 0.0) + 0.2},
                "BS": {"deger": self.ham_veri.get("BS", 0.0) + 0.1},
                "NS": {"deger": self.ham_veri.get("NS", 0.0) + 0.3},
                "RS": {"deger": self.ham_veri.get("RS", 0.0) + 0.05},
                "G": {"deger": self.ham_veri.get("G", 0.0) + 0.15},
            },
            "d4": {  # 2 birim sonra (d2'den 2 birim sonra)
                "TS": {"deger": self.ham_veri.get("TS", 0.0) + 0.5},
                "BS": {"deger": self.ham_veri.get("BS", 0.0) + 0.3},
                "NS": {"deger": self.ham_veri.get("NS", 0.0) + 0.8},
                "RS": {"deger": self.ham_veri.get("RS", 0.0) + 0.2},
                "G": {"deger": self.ham_veri.get("G", 0.0) + 0.6},
            },
        }
        return zaman_noktalari

    def _anh(self, deger: float, zaman: str) -> float:
        """
        Ardışık Nokta Hesaplaması (ANH) uygular.

        Args:
            deger (float): İşlenecek değer.
            zaman (str): Değerin ait olduğu zaman (örn. "d2" veya "d0-d2").

        Returns:
            float: ANH uygulanmış değer.
        """
        # Örnek ANH formülü (Gerçek formülünüzü buraya girin)
        if "-" in zaman:  # Zaman aralığı ise
            zaman_baslangici, zaman_bitisi = zaman.split("-")
            zaman_degeri = int(zaman_bitisi[1:]) - int(zaman_baslangici[1:])  # Aralık uzunluğunu al
        else:  # Tekil zaman noktası ise
            zaman_degeri = int(zaman[1:])  # "d2" -> 2
        return deger * 1.1 + zaman_degeri * 0.05

    def _hm(self, deger: float, zaman_araligi: str) -> float:
        """
        Home Metodu (HM) uygular.

        Args:
            deger (float): İşlenecek değer.
            zaman_araligi (str): Değerin ait olduğu zaman aralığı (örn. "d0-d2").

        Returns:
            float: HM uygulanmış değer.
        """
        # Örnek HM formülü (Gerçek formülünüzü buraya girin)
        zaman_baslangici_str, zaman_bitisi_str = zaman_araligi.split("-")  # "d0-d2" -> "d0", "d2"
        zaman_baslangici = int(zaman_baslangici_str[1:])  # "d0" -> 0
        zaman_bitisi = int(zaman_bitisi_str[1:])  # "d2" -> 2
        return deger * 0.9 + (zaman_bitisi - zaman_baslangici) * 0.1

    def calculate_all(self) -> Dict[str, Any]:
        """
        Tüm hesaplamaları yapar ve sonuçları düzenler.

        Returns:
            Dict[str, Any]: Düzenlenmiş sonuçlar.
        """

        cikti = {
            "ham_veri_konumu": self.ham_veri_konumu,
            "I_degerleri": {
                "TS": [],
                "BS": [],
                "NS": [],
                "RS": [],
                "G": []
            },
            "M_degerleri": {
                "TS": [],
                "BS": [],
                "NS": [],
                "RS": [],
                "G": []
            },
            "AS_degerleri": {
                "TS": [],
                "BS": [],
                "NS": [],
                "RS": [],
                "G": []
            }
        }

        zamanlar = sorted([int(z[1:]) for z in self.zaman_noktalari.keys()])  # Zamanları sırala (d2 -> 2)
        for i, zaman in enumerate(zamanlar):
            zaman_str = f"d{zaman}"
            skorlar = self.zaman_noktalari[zaman_str]

            for skor_adi, skor_degeri in skorlar.items():
                deger = skor_degeri["deger"]

                # I değerleri (ANH'den nokta zamanlı geçirilmiş)
                i_degeri = self._anh(deger, zaman_str)
                cikti["I_degerleri"][skor_adi].append({"zaman": zaman_str, "zaman": zaman_str, "deger": i_degeri})

                # M değerleri (ANH'den aralık zamanlı geçirilmiş)
                if i > 0:
                    onceki_zaman_indeksi = i - 1
                    onceki_zaman = f"d{zamanlar[onceki_zaman_indeksi]}"
                    zaman_araligi = f"{onceki_zaman}-{zaman_str}"
                    m_degeri = self._anh(deger, zaman_araligi)  # ANH'ye zaman aralığı gönderiliyor
                    cikti["M_degerleri"][skor_adi].append({"zaman_araligi": zaman_araligi, "deger": zaman_araligi, "deger": m_degeri})

                    # AS değerleri (ANH ve HM'den geçirilmiş)
                    as_degeri = self._hm(m_degeri, zaman_araligi)  # HM'ye M değeri gönderiliyor
                    cikti["AS_degerleri"][skor_adi].append({"zaman_araligi": zaman_araligi, "deger": zaman_araligi, "deger": as_degeri})
                else:
                    # Başlangıç zamanı için M ve AS değerleri yok
                    cikti["M_degerleri"][skor_adi].append({"zaman_araligi": "Yok", "deger": 0.0})
                    cikti["AS_degerleri"][skor_adi].append({"zaman_araligi": "Yok", "deger": 0.0})

        return cikti

    def write_output(self, output_file_path: str):
        """
        Çıktı verisini JSON dosyasına yazar.

        Args:
            output_file_path (str): Çıktı dosyasının konumu.
        """
        try:
            with open(output_file_path, "w") as f:
                json.dump(self.calculate_all(), f, indent=4)
            logging.info(f"Çıktı dosyası başarıyla oluşturuldu: {output_file_path}")
        except Exception as e:
            logging.error(f"Çıktı dosyası oluşturulurken hata oluştu: {e}")

if __name__ == "__main__":
    # Örnek ham veri (core.py'den geldiğini varsayalım)
    ham_veri = {
        "TS": 0.1,
        "BS": 0.2,
        "NS": 0.3,
        "RS": 0.05,
        "G": 0.2
    }
    input_file_path = "input.json"  # Örnek dosya adı
    calculator = Calculator(ham_veri, input_file_path)
    cikti = calculator.calculate_all()
    print(json.dumps(cikti, indent=4))  # Konsola yazdır
    calculator.write_output("output.json")  # Dosyaya yazdır