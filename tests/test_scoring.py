import unittest
from mafia_bot.scoring import calculate

class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.roles = {n: "red" for n in range(1,11)}
        self.roles.update({4:"sheriff",7:"don",8:"mafia",9:"mafia"})

    def test_nomination_vote_and_will(self):
        events = [
            dict(id="a",kind="nomination",actor=10,targets=[7]),
            dict(id="b",kind="vote",actor=5,targets=[8]),
            dict(id="c",kind="will",actor=1,targets=[3,7,8]),
        ]
        scores,entries,pending = calculate(self.roles,events)
        self.assertEqual(scores[10],3)
        self.assertEqual(scores[5],2)
        self.assertEqual(scores[1],3)
        self.assertEqual(scores[3],-1)
        self.assertEqual(scores[7],-1)
        self.assertEqual(scores[8],-1)
        self.assertEqual(pending,[])

    def test_black_will_no_points(self):
        scores,_,pending = calculate(self.roles,[dict(id="x",kind="will",actor=8,targets=[1,2,3])])
        self.assertTrue(all(x==0 for x in scores.values()))
        self.assertFalse(pending)

    def test_unknown_roles_pending(self):
        self.roles[8]="unknown"
        scores,_,pending=calculate(self.roles,[dict(id="x",kind="nomination",actor=5,targets=[8])])
        self.assertEqual(pending,["x"])
        self.assertEqual(scores[5],0)

    def test_black_vote_is_unscored(self):
        scores,_,pending=calculate(self.roles,[dict(id="x",kind="vote",actor=8,targets=[1])])
        self.assertEqual(pending,["x"])
        self.assertEqual(scores[8],0)

if __name__=="__main__":
    unittest.main()
