from os import sys, path, environ

# If NOT runnning using `python manage.py test`, then uncomment following two line
# sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
# environ["DJANGO_SETTINGS_MODULE"] = 'pgd.settings'

from pgd_core.models import Protein, Chain, Residue

from django.test import TestCase , Client

class OccupancyTestCase(TestCase):
    def __init__(self):
        self.residues = Residue.objects.all()

    def setUp(self):
        # Called when run as `python manage.py test`
        self.residues = Residue.objects.all()
        
    def test_occm_valid(self):
        # All Occm should always be between 0.0 and 1.0 (Inclusive) and should never be None
       
        for i in self.residues:
           # Occm is not None AND Occm<=1 AND Occm>=0.0
            self.assertIsNotNone(i.occscs) and self.assertLessequal(i.occm,1.0) and self.assertGreaterEqual(i.occm, 0.0)

    def test_occsc_valid(self):
        # All Occscs value should be between 0.0 and 1.0 (Inclusive) and should never be None

        for i in self.residues:
            # Occscs is not None AND Occscs<=1 AND Occscss>=0.0
            self.assertIsNotNone(i.occscs) and self.assertLessequal(i.occscs,1.0) and self.assertGreaterEqual(i.occscs, 0.0)

    def test_occsc_1_for_GLY(self):
        # Occsc value for GLYCINE should be 1.0
        # REF: https://code.osuosl.org/issues/17565
        
        for i in self.residues:
            
            if i.aa == "Gly":
                self.assertEqual(i.occscs,1.0)

    def test_occsc_1_for_ALA(self):
        # Occsc value for ALANINE should be 1.0
        # REF: https://code.osuosl.org/issues/17565
        
        for i in self.residues:
            if i.aa == "Ala":
                self.assertEqual(i.occscs,1.0)

    def start_test(self):
        test_occm_valid()
        test_occsc_valid()
        test_occsc_1_for_GLY()
        test_occsc_1_for_ALA()
        

if __name__ == "__main__":
    a = OccupancyTestCase()
    a.start_test()