from typing import Tuple, List, Optional

class QualityGateValidator:
    """Memvalidasi pemahaman AI agar memenuhi Kontrak 6 Pilar Literasi Tinggi."""

    @staticmethod
    def validate_enrichment(
        purpose: str,
        logic_phases: List[str],
        colloquial_aliases: List[str],
        existing_purpose: str = "",
        existing_phases_count: int = 0,
        existing_aliases_count: int = 0
    ) -> Tuple[bool, List[str]]:
        errors = []

        eff_purpose = purpose.strip() if purpose.strip() else existing_purpose.strip()
        if len(eff_purpose) < 20:
            errors.append("Tujuan/Purpose terlalu pendek (minimal 20 karakter penjelasan fungsional).")

        total_aliases = len(colloquial_aliases) + existing_aliases_count
        if total_aliases < 3:
            errors.append(f"Kamus istilah awam pengguna kurang (minimal 3 istilah, ditemukan total: {total_aliases}).")

        total_phases = len(logic_phases) + existing_phases_count
        if total_phases < 2:
            errors.append(f"Daftar fase logika internal terlalu sedikit (minimal 2 fase, ditemukan total: {total_phases}).")

        is_valid = len(errors) == 0
        return is_valid, errors
