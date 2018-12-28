import os
import json
import brutal_force
import apriori
import fp_growth

def frequent_itemset_compare(ground_truth, target):
    for f_itemset in target:
        assert f_itemset in ground_truth, 'frequent itemset is not the same.'

def association_rule_compare(ground_truth, target):
    for rule in target:
        assert rule in ground_truth, 'association rule is not the same.'

data_path = os.path.dirname(os.path.abspath(__file__)) + '/data'
data_name = '/example.json'

f = open(data_path + data_name, 'r')
transactions = json.loads(f.read())
f.close()

min_sup = 0.4
min_cof = 0.5

bf = brutal_force.AssociationRuleMining(transactions=transactions, min_sup=min_sup, min_cof=min_cof)
ap = apriori.AssociationRuleMining(transactions=transactions, min_sup=min_sup, min_cof=min_cof)
fp = fp_growth.AssociationRuleMining(transactions=transactions, min_sup=min_sup, min_cof=min_cof)

print('brutal force versus apriori')
frequent_itemset_compare(bf.frequent_itemset(), ap.frequent_itemset())
frequent_itemset_compare(ap.frequent_itemset(), bf.frequent_itemset())
association_rule_compare(bf.association_rules(), ap.association_rules())
association_rule_compare(ap.association_rules(), bf.association_rules())
print('same')

print('brutal force versus fp-growth')
frequent_itemset_compare(bf.frequent_itemset(), fp.frequent_itemset())
frequent_itemset_compare(fp.frequent_itemset(), bf.frequent_itemset())
association_rule_compare(bf.association_rules(), fp.association_rules())
association_rule_compare(fp.association_rules(), bf.association_rules())
print('same')
