import tempfile, unittest
from pathlib import Path
from quarry_core import scan,layout_treemap
class QuarryTests(unittest.TestCase):
    def test_scan_aggregates(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'a').mkdir();(p/'a'/'x.bin').write_bytes(b'x'*10);(p/'b.txt').write_bytes(b'y'*5)
            r=scan(p);self.assertEqual(r.file_count,2);self.assertEqual(r.total_bytes,15);self.assertEqual(r.by_top['a'],10);self.assertEqual(r.by_ext['.bin'],10)
    def test_treemap_preserves_area(self):
        r=layout_treemap([('a',3),('b',1)],0,0,100,40);self.assertAlmostEqual(sum(x[4]*x[5] for x in r),4000)
if __name__=='__main__':unittest.main()