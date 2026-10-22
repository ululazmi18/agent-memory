from typing import Tuple, List

class QualityGateValidator:
    """Memvalidasi pemahaman AI agar memenuhi Kontrak 6 Pilar Literasi Tinggi."""

    @staticmethod
    def validate_enrichment(
        purpose: str,
        logic_phases: List[str],
        colloquial_aliases: List[str],
        upstream: str = "",
        downstream: str = "",
        guardrails: str = ""
    ) -> Tuple[bool, List[str]]:
        errors = []

        if len(purpose.strip()) < 20:
            errors.append("Tujuan/Purpose terlalu pendek (minimal 20 karakter penjelasan fungsional).")

        if len(colloquial_aliases) < 3:
            errors.append(f"Kamus istilah awam pengguna kurang (minimal 3 istilah, ditemukan: {len(colloquial_aliases)}).")

        if len(logic_phases) < 2:
            errors.append(f"Daftar fase logika internal terlalu sedikit (minimal 2 fase, ditemukan: {len(logic_phases)}).")

        is_valid = len(errors) == 0
        return is_valid, errors
