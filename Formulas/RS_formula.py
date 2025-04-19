def calculate_RS(Pradiation, Pref):
    """
    Radyasyon Skorunu (RS) hesaplar.

    Args:
        Pradiation: Radyasyon dozu
        Pref: Referans radyasyon dozu

    Returns:
        float: Hesaplanan Radyasyon Skoru (RS)
    """
    rs = (Pradiation / Pref)
    return rs
