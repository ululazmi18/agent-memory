import unittest
from agent_memory.core.validator import QualityGateValidator

class TestValidator(unittest.TestCase):
    def test_valid_enrichment(self):
        is_valid, errors = QualityGateValidator.validate_enrichment(
            purpose="Manages user session tokens and validates JWT headers.",
            logic_phases=["Extract token", "Verify cryptographic signature"],
            colloquial_aliases=["cek login", "auth token", "validasi sesi"]
        )
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_purpose_too_short(self):
        is_valid, errors = QualityGateValidator.validate_enrichment(
            purpose="Short",
            logic_phases=["Phase 1", "Phase 2"],
            colloquial_aliases=["alias 1", "alias 2", "alias 3"]
        )
        self.assertFalse(is_valid)
        self.assertTrue(any("terlalu pendek" in e for e in errors))

    def test_insufficient_aliases(self):
        is_valid, errors = QualityGateValidator.validate_enrichment(
            purpose="Valid purpose with sufficient length for testing.",
            logic_phases=["Phase 1", "Phase 2"],
            colloquial_aliases=["only one"]
        )
        self.assertFalse(is_valid)
        self.assertTrue(any("Kamus istilah awam" in e for e in errors))

    def test_insufficient_phases(self):
        is_valid, errors = QualityGateValidator.validate_enrichment(
            purpose="Valid purpose with sufficient length for testing.",
            logic_phases=["Only single phase"],
            colloquial_aliases=["alias 1", "alias 2", "alias 3"]
        )
        self.assertFalse(is_valid)
        self.assertTrue(any("fase logika" in e for e in errors))

    def test_granular_update_with_existing_context(self):
        # Empty purpose sent, but existing_purpose has valid length
        is_valid, errors = QualityGateValidator.validate_enrichment(
            purpose="",
            logic_phases=["New Phase"],
            colloquial_aliases=["new alias"],
            existing_purpose="Existing high-density description from previous inspection.",
            existing_phases_count=1,
            existing_aliases_count=2
        )
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

if __name__ == "__main__":
    unittest.main()
