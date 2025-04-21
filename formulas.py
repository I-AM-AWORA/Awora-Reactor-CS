"""
formulas.py

Awora-FLX formülündeki skorları hesaplayan fonksiyonlar.
"""

def calculate_ts(dT: float, Qnet: float, delT: float, dTref: float, Qref: float, delTref: float) -> float:
    """
    Termal skoru hesaplar.

    Args:
        dT: Isı farkı.
        Qnet: Isı akışı.
        delT: Isı gradyanı.
        dTref: Referans ısı farkı.
        Qref: Referans ısı akışı.
        delTref: Referans ısı gradyanı.

    Returns:
        Termal skor (TS).
    """
    ts = 0.0
    if dTref != 0.0:
        ts += dT / dTref
    if Qref != 0.0:
        ts += Qnet / Qref
    if delTref != 0.0:
        ts += delT / delTref
    return ts  # [cite: 7, 8, 9, 10, 11]


def calculate_bs(dP: float, sigma: float, dPref: float, sigmaref: float) -> float:
    """
    Basınç skorunu hesaplar.

    Args:
        dP: Basınç farkı.
        sigma: Malzemenin gerilimi.
        dPref: Referans basınç farkı.
        sigmaref: Referans gerilimi.

    Returns:
        Basınç skoru (BS).
    """
    bs = 0.0
    if dPref != 0.0:
        bs += dP / dPref
    if sigmaref != 0.0:
        bs += sigma / sigmaref
    return bs  # [cite: 11, 12, 13]


def calculate_ns(neutron_flux: float, keff: float, neutron_flux_ref: float, keff_ref: float) -> float:
    """
    Nötron skorunu hesaplar.

    Args:
        neutron_flux: Nötron akışı.
        keff: Fizyon zincir reaksiyonu verimliliği.
        neutron_flux_ref: Referans nötron akışı.
        keff_ref: Referans fizyon zincir reaksiyonu verimliliği.

    Returns:
        Nötron skoru (NS).
    """
    ns = 0.0
    if neutron_flux_ref != 0.0:
        ns += neutron_flux / neutron_flux_ref
    if keff_ref != 0.0:
        ns += keff / keff_ref
    return ns  # [cite: 13, 14]


def calculate_rs(radiation_dose: float, radiation_dose_ref: float, Pradiation: float, Pref: float) -> float:
    """
    Radyasyon skorunu hesaplar.

    Args:
        radiation_dose: Radyasyon dozu.
        radiation_dose_ref: Referans radyasyon dozu.
         Pradiation: hesaplanmış radyasyon dozu
         Pref: referans radyasyon dozu

    Returns:
        Radyasyon skoru (RS).
    """
    rs = 0.0
    if radiation_dose_ref != 0.0:
        rs += radiation_dose / radiation_dose_ref

    if Pref != 0.0:
        rs += Pradiation / Pref

    return rs  # [cite: 15, 16, 17]


def calculate_anh(G: float) -> float:
    """
    Ana skor hesaplaması (HM formülü).

    Args:
        G: Ağırlıklandırılmış skor.

    Returns:
        Ana skor (ANH).
    """

    return G  # Şu an sadece G'yi döndürüyor, HM formülü detayları belirsiz. [cite: 57, 58, 59, 60, 61, 62, 63]


# Diferansiyel denklemler (şimdilik sadece tanımlar) [cite: 19, 20, 21, 22, 23, 24, 25]
def dts_dt(ts: float, ns: float, DT: float, alpha: float, beta: float,nabla2TS: float) -> float:
    """Termal diferansiyel denklemi."""
    return DT*nabla2TS + alpha * ts * ns - beta * ns


def dbs_dt(bs: float, ts: float, deltaP: float, gamma: float, lambda_: float, delta: float) -> float:
    """Basınç diferansiyel denklemi."""

    return gamma * (deltaP + lambda_ * ts) - delta * bs**2


def dns_dt(ns: float, ts: float, epsilon: float, phi: float, zeta: float) -> float:
    """Nötron diferansiyel denklemi."""
    return epsilon + phi - zeta * ns * ts


def drs_dt(rs: float, Rdose: float, eta: float, theta: float) -> float:
    """Radyasyon diferansiyel denklemi."""

    return eta * Rdose - theta * rs