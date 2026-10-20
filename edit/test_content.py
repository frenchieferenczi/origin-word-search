"""Content tests for the Word Search rotation. Run from the repo root:  python3 -m unittest discover -s edit -v"""
import json, random, re, sys, unittest, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'edit'))
from bundle import enc, split

SRC = (ROOT / 'edit/template.html').read_text()
DEFAULT = json.loads(re.search(r'/\*DEFAULT\*/(.*?)/\*END\*/', SRC, re.S).group(1))
SCHEDULE = json.loads(re.search(r'/\*SCHEDULE\*/(.*?)/\*END\*/', SRC, re.S).group(1))
ALL = [DEFAULT] + SCHEDULE
SIZE = int(re.search(r'const SIZE = (\d+)', SRC).group(1))

def pick(today):
    p = DEFAULT
    for w in SCHEDULE:
        if w['start'] <= today: p = w
    return p

class Puzzles(unittest.TestCase):
    def test_sixteen_unique_words_each(self):
        for w in ALL:
            words = [x['word'] for x in w['words']]
            self.assertEqual(len(words), 16, w['title']); self.assertEqual(len(set(words)), 16, w['title'])

    def test_labels_and_grid_boundary(self):
        for w in ALL:
            for x in w['words']:
                self.assertRegex(x['word'], r'^[A-Z]{2,%d}$' % SIZE)
                self.assertEqual(re.sub(r'[^A-Z]', '', x['label'].upper()), x['word'], x)

    def test_no_word_repeats_across_weeks(self):
        seen = set()
        for w in ALL:
            for x in w['words']:
                self.assertNotIn(x['word'], seen, x); seen.add(x['word'])

    def test_every_week_fills_reliably(self):
        """Port of buildGrid(): with 50 rebuilds the chance of a missing word must be ~0 for every week."""
        DIRS = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        rng = random.Random(7)
        for w in ALL:
            words = sorted((x['word'] for x in w['words']), key=len, reverse=True); ok = 0; N = 150
            for _ in range(N):
                g = [['']*SIZE for _ in range(SIZE)]; placed = 0
                for word in words:
                    for _ in range(400):
                        dr, dc = rng.choice(DIRS); r, c = rng.randrange(SIZE), rng.randrange(SIZE)
                        er, ec = r+dr*(len(word)-1), c+dc*(len(word)-1)
                        if not (0 <= er < SIZE and 0 <= ec < SIZE): continue
                        cells = [(r+dr*i, c+dc*i) for i in range(len(word))]
                        if all(g[a][b] in ('', word[i]) for i, (a, b) in enumerate(cells)):
                            for i, (a, b) in enumerate(cells): g[a][b] = word[i]
                            placed += 1; break
                ok += placed == len(words)
            self.assertLess((1 - ok / N) ** 50, 1e-9, w['title'])

class Rotation(unittest.TestCase):
    def test_weekly_mondays_in_order(self):
        ds = [datetime.date.fromisoformat(w['start']) for w in SCHEDULE]
        self.assertEqual(len(ds), 16)
        for a, b in zip(ds, ds[1:]): self.assertEqual((b - a).days, 7)
        self.assertTrue(all(d.weekday() == 0 for d in ds))

    def test_pick_boundaries(self):
        self.assertIs(pick('2026-10-25'), DEFAULT)
        self.assertIs(pick(SCHEDULE[0]['start']), SCHEDULE[0])
        self.assertIs(pick('2027-06-01'), SCHEDULE[-1])

    def test_template_wiring(self):
        for s in ['WEEK = this.pickWeek();', 'WORDS = this.WEEK.words;', '{{ title }}', '{{ banner }}', '{{ doneMsg }}',
                  'if (this.buildGrid()) return;']:
            self.assertIn(s, SRC)

class Fields(unittest.TestCase):
    def test_every_constant_used_is_defined(self):
        """Catches a field dropped while editing (e.g. HEX_POSITIONS): every this.UPPER_CASE must be declared."""
        used = set(re.findall(r'this\.([A-Z][A-Z_]+)\b', SRC))
        declared = set(re.findall(r'^  ([A-Z][A-Z_]+) = ', SRC, re.M))
        self.assertEqual(used - declared, set())

class Bundle(unittest.TestCase):
    def test_index_matches_template(self):
        s = (ROOT / 'index.html').read_text(); m = split(s)
        self.assertEqual(json.loads(m.group(2)), SRC)
        self.assertEqual(enc(json.loads(m.group(2))), m.group(2))
        self.assertNotIn('</script', m.group(2))

    def test_duplicate_page_in_sync(self):
        self.assertEqual((ROOT / 'index.html').read_bytes(), (ROOT / 'Pelvic Floor Word Search.html').read_bytes())

if __name__ == '__main__':
    unittest.main()
