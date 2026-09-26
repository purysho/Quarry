import json, os, tempfile, time, unittest
from pathlib import Path

from quarry_core import export_json, largest_files, layout_treemap, scan


class QuarryBehaviourTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(); self.root = Path(self._tmp.name)
    def tearDown(self):
        self._tmp.cleanup()

    def put(self, rel, size, age_days=0):
        p = self.root / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b'x' * size)
        t = time.time() - age_days * 86400; os.utime(p, (t, t)); return p

    def test_largest_files_are_sorted_descending_and_limited(self):
        for i, size in enumerate([5, 50, 500, 1]): self.put(f'f{i}.bin', size)
        r = scan(self.root)
        self.assertEqual([f.size for f in largest_files(r, 3)], [500, 50, 5])

    def test_files_without_extension_are_labelled(self):
        self.put('Makefile', 7)
        self.assertEqual(scan(self.root).by_ext, {'[no extension]': 7})

    def test_extensions_are_case_insensitive(self):
        self.put('a.JPG', 3); self.put('b.jpg', 4)
        self.assertEqual(scan(self.root).by_ext, {'.jpg': 7})

    def test_age_buckets(self):
        self.put('new.log', 1, 1); self.put('mid.log', 2, 90); self.put('year.log', 4, 300); self.put('ancient.log', 8, 800)
        self.assertEqual(scan(self.root).by_age, {'≤30d': 1, '31–180d': 2, '181–365d': 4, '>1y': 8})

    def test_ignored_directories_and_symlinks_are_not_counted(self):
        real = self.put('real.bin', 10); self.put('node_modules/dep.js', 1000); self.put('.git/objects/pack', 1000)
        try:
            (self.root / 'link.bin').symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks unavailable')
        r = scan(self.root)
        self.assertEqual((r.file_count, r.total_bytes), (1, 10))

    def test_top_level_totals_are_sorted_largest_first(self):
        self.put('small/a', 1); self.put('big/a', 100); self.put('big/deep/b', 100)
        self.assertEqual(list(scan(self.root).by_top.items()), [('big', 200), ('small', 1)])

    def test_treemap_splits_along_the_longer_side_and_handles_empty_input(self):
        wide = layout_treemap([('a', 1), ('b', 1)], 0, 0, 200, 50)
        self.assertEqual([round(r[4]) for r in wide], [100, 100])
        tall = layout_treemap([('a', 1), ('b', 3)], 0, 0, 50, 200)
        self.assertEqual([round(r[5]) for r in tall], [50, 150])
        self.assertEqual(layout_treemap([], 0, 0, 10, 10), [])
        self.assertEqual(layout_treemap([('z', 0)], 0, 0, 10, 10), [])

    def test_export_json_is_loadable(self):
        self.put('a.txt', 3)
        with tempfile.TemporaryDirectory() as out:
            path = Path(out) / 'r.json'; export_json(scan(self.root), path)
            self.assertEqual(json.loads(path.read_text())['total_bytes'], 3)


if __name__ == '__main__':
    unittest.main()
