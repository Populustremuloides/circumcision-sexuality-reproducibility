import unittest
from validation.diagnostics import failure_signature as signature
class DiagnosticChecks(unittest.TestCase):
    def test_rounding(self):
        self.assertEqual(signature('Unstable information matrix, condition=2.2398e+13'), signature('Unstable information matrix, condition=2.2401e+13'))
    def test_threshold(self):
        with self.assertRaises(AssertionError):signature('Unstable information matrix, condition=1e+8')
    def test_category(self):
        self.assertNotEqual(signature('GLM did not converge'), signature('Unstable information matrix, condition=2e+13'))
    def test_psu(self):
        self.assertNotEqual(signature('[{"deleted_psu":"a","error":"GLM did not converge"}]'),signature('[{"deleted_psu":"b","error":"GLM did not converge"}]'))
    def test_missing(self):
        self.assertIsNone(signature(float('nan')))
if __name__=='__main__':unittest.main()
