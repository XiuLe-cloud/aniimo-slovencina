import unittest
from pipeline.qa import check

class QARegressionTests(unittest.TestCase):
    def errors(self,en,sk):
        return [x for x in check('1',en,sk,{'terms':[]}) if x['severity']=='ERROR']
    def test_numbered_list_boundary(self):
        self.assertFalse(self.errors('Activity\n3. Rewards','Činnosť\n3. Odmeny'))
        self.assertTrue(self.errors('Activity\n3. Rewards','Činnosť\n4. Odmeny'))
    def test_grouped_numbers(self):
        self.assertFalse(self.errors('Receive 1,000 EXP','Získaj 1 000 EXP'))
        self.assertFalse(self.errors('Receive 1,000 EXP','Získaj 1,000 EXP'))
        self.assertTrue(self.errors('Receive 1,000 EXP','Získaj 100 EXP'))
    def test_color_text_and_input_tokens(self):
        self.assertFalse(self.errors('#cd89c28red#z','#cd89c28červená#z'))
        self.assertTrue(self.errors('#cd89c28red#z','#cd89c29červená#z'))
        self.assertTrue(self.errors('#kCatch/Throw#z','#kCatch/Thrrow#z'))
    def test_prose_bracket_not_placeholder(self):
        self.assertFalse(self.errors('[Operation: Egg Heist]','[Operácia: Lúpež vajec]'))
    def test_chinese_time_numbers(self):
        self.assertFalse(self.errors('5时30分','5 h 30 min'))
        self.assertTrue(self.errors('5时30分','5 h 40 min'))

if __name__=='__main__':unittest.main()
