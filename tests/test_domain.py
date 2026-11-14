import copy
import unittest
from app import domain
from app.service import load_study


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.data = load_study()
        self.request = {'operation': 'draft', 'slots': 12, 'arm': 'peer'}

    def test_capacity_is_enforced(self):
        data = copy.deepcopy(self.data)
        data['capacity']['budget'] = 5
        data['capacity']['slot_cost']['peer'] = 3
        result = domain.act(data, self.request)
        self.assertEqual(len(result['students']), 1)
        self.assertEqual(result['cost'], 3)

    def test_pending_is_not_zero_outcome(self):
        data = copy.deepcopy(self.data)
        data['trial'][0]['outcome_available_at'] = '2099-01-01'
        data['trial'][0]['outcome'] = 0
        self.assertEqual(len(domain.mature_trial(data)), len(domain.mature_trial(self.data)) - 1)

    def test_impossible_assignment_is_rejected(self):
        data = copy.deepcopy(self.data)
        row = data['trial'][0]
        row['propensities'][row['invited_arm']] = 0
        with self.assertRaises(ValueError):
            domain.baseline(data)


if __name__ == '__main__':
    unittest.main()
