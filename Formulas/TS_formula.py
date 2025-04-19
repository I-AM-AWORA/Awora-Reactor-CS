def calculate_TS(dT, Qnet, delT, dTref, Qref, delTref):
    """
    Termal Skoru (TS) hesaplar.

    Args:
        dT: Sıcaklık farkı
        Qnet: Isı akışı
        delT: Sıcaklık gradyanı
        dTref: Referans sıcaklık farkı
        Qref: Referans ısı akışı
        delTref: Referans sıcaklık gradyanı

    Returns:
        float: Hesaplanan Termal Skor (TS)
    """
    ts = (dT / dTref) + (Qnet / Qref) + (delT / delTref)
    return ts
