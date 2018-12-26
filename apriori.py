"""Module for association rules generation.

Use class `AssociationRuleMining` to generate association rules,
see test section for code example.
"""

from encoder import StringToIntegerEncoder, ListToIntegerEncoder

class AssociationRuleMining:
    """Generate association rule with Apriori algorithm.

    This class use Apriori algorithm to speed up frequent itemsets generation,
    thus speed up association rule generation.
    """

    def __init__(self, transactions=None, min_sup=0.1, min_cof=0.1, max_k=0):
        """Initialize settings for association rule mining.

        Args:
            transactions （list of list of item):
                Transaction database.
            min_sup (float):
                Minimum support for frequent itemset.
            min_cof (float):
                Minimum confidence for association rule.
            max_k (int):
                Maximum size for freuent itemset (k-itemset).
        """

        self.__min_sup = min_sup
        self.__min_cof = min_cof
        self.__sup_count = {}
        self.__frequent_k_itemset = {}
        self.__association_rules = []
        self.__item_encoder = StringToIntegerEncoder()
        self.__itemset_encoder = ListToIntegerEncoder()
        self.__transactions = transactions

        # Encode transactions to speed up calculation.
        self.__encoded_transactions = (self
                                       .__item_encoder
                                       .encode_from_list_of_string_list(transactions))
        self.__n_transactions = len(transactions)
        self.__max_k = max_k
        if self.__max_k <= 0:
            for transaction in self.__transactions:
                if self.__max_k < len(transaction):
                    self.__max_k = len(transaction)

    @staticmethod
    def __join(itemset_1, itemset_2):
        """Join two k-1-itemset to form k-itemset.

        Args:
            itemset_1 (list of item): k-1-itemset.
            itemset_2 (list of item): k-1-itemset.

        Returns:
            list of items: Joint k-itemset.
        """
        join_itemset = list(set(itemset_1) | set(itemset_2))
        join_itemset.sort()
        return join_itemset

    @staticmethod
    def __split_itemset(itemset):
        """All possible way of spliting itemset into two smaller itemset.

        Same problem as 2 equivalent class,
        number of possible combination is Stiring number of second kind S(k, 2).
        This method is intended to be private.

        Args:
            itemset (list of item):
                Target itemset to be splited.

        Returns:
            list of tuple of list of itemset:
                All possible combination of two smaller itemset.
        """

        # Recursive end condition.
        if len(itemset) == 2:
            return [([itemset[0]], [itemset[1]])]

        all_split = []

        # First way to split: 1-itemset & k-1-items
        all_split.append(([itemset[0]], itemset[1:]))
        for front, back in AssociationRuleMining.__split_itemset(itemset[1:]):
            # Second way to split: 1-itemset + k-n-1-itemset & n-itemset
            # Keep order by put 1-itemset at front.
            new_split1 = ([itemset[0]]+front, back)

            # Third way to split: k-n-1-itemset & 1-itemset + n-itemset
            # Keep order by put 1-itemset at front.
            new_split2 = (front, [itemset[0]]+back)
            all_split.append(new_split1)
            all_split.append(new_split2)
        return all_split

    def support_count(self, itemset):
        """Support count for the itemset.

        The input itemset will first be encoded element-wised (encode each item),
        then be encoded list-wised (encode the encoded itemset).
        Using the enocded result to count support throught out the encoded transaction.
        If itemset is already encoded before input,
        it will be given a zero support count as return.

        Args:
            itemset (list of item):
                Item cannot be encoded form.

        Returns:
            int:
                Support count for the given itemset.
        """

        # Encode items in itemset.
        itemset = self.__item_encoder.encode_from_string_list(itemset)

        # Encode itemset.
        encoded_itemset = self.__itemset_encoder.encode_from_list(itemset)

        # If already calculated before, skip the calculation process.
        if encoded_itemset in self.__sup_count:
            pass
        # Else enumerate all transactions to do support count.
        else:
            self.__sup_count[encoded_itemset] = 0
            for transaction in self.__encoded_transactions:
                if all(map(lambda item: item in transaction, itemset)):
                    self.__sup_count[encoded_itemset] = self.__sup_count[encoded_itemset] + 1

        # Support count cached result.
        return self.__sup_count[encoded_itemset]

    def support(self, itemset):
        """Support for the itemset.

        Calculate the ratio of itemset appeared in all transaction.
        If itemset is already encoded before input,
        it will be given a zero support as return.

        Args:
            itemset (list of item):
                Item cannot be encoded form.

        Returns:
            int:
                Support for the given itemset.
        """

        return self.support_count(itemset) / self.__n_transactions

    def confidence(self, itemset_1, itemset_2):
        """Confidence of association rule `itemset_1` -> `itemset_2`.

        If `itemset_`1 or `itemset_2` is already encoded before input,
        it will be given a zero confidence as return.

        Args:
            itemset_1 (list of item):
                Denominator of confidence formula.
            itemset_2 (list of item):
                Combine with `itemset_1` to form nominator of confidence formula.

        Returns:
            float:
                Confidence of the given association rule.
        """

        return self.support_count(itemset_1 + itemset_2) / self.support_count(itemset_1)

    def frequent_k_itemset(self, k=1):
        """Frequent k-itemset of the transactions.

        If support of an k-itemset is greater than minimum support threshold,
        it will be in the list of frequent k-itemset.
        Using Apriori algorithm to generate candidate frequent itemsets.

        Args:
            k (int):
                size of frequent itemset

        Returns:
            list of k-itemset:
                Itemsets in list are frequent k-itemset.

        Raises:
            ValueError:
                Valid range of k should be 0 < k <= self.max_k.
        """

        # Validation for k.
        if k <= 0:
            raise ValueError('k should be greater than 0.')
        if k > self.__max_k:
            raise ValueError('k should be smaller than or equal to max_k={}.'.format(self.__max_k))

        # If already calculated before, skip the calculation process.
        if k in self.__frequent_k_itemset:
            pass
        # Else if k is 1, directly enumerate frequent 1-itemset.
        elif k == 1:
            self.__frequent_k_itemset[1] = set()
            for transaction in self.__encoded_transactions:
                for item in transaction:
                    one_itemset = [item]
                    decoded_1_itemset = self.__item_encoder.decode_to_string_list(one_itemset)
                    if self.support(decoded_1_itemset) >= self.__min_sup:
                        (self
                         .__frequent_k_itemset[1]
                         .add(self.__itemset_encoder.encode_from_list(one_itemset)))
        # Else use Apriori algorithm to generate frequent k-itemset.
        else:
            self.__frequent_k_itemset[k] = set()
            # Get frequent k-1-itemset.
            frequent_k_1_itemset = list(self.__frequent_k_itemset[k-1])

            # Number of frequent k-1-itemset.
            n_of_k_1_itemset = len(frequent_k_1_itemset)

            # Enumerate all possible combination of two frequent k-1-itemsets to form k-itemset.
            for i in range(n_of_k_1_itemset-1):
                k_1_itemset_1 = self.__itemset_encoder.decode_to_list(frequent_k_1_itemset[i])
                for j in range(i+1, n_of_k_1_itemset):
                    k_1_itemset_2 = self.__itemset_encoder.decode_to_list(frequent_k_1_itemset[j])

                    # Skip if joint itemset size is not equal to k.
                    if len(set(k_1_itemset_1) & set(k_1_itemset_2)) != k-2:
                        continue

                    # Join two frequent k-1-itemsets to form k-itemset.
                    candidate_k_itemset = AssociationRuleMining.__join(k_1_itemset_1, k_1_itemset_2)

                    # Decode items in itemset because support function need items to be decoded.
                    decoded_candidate_k_itemset = (self
                                                   .__item_encoder
                                                   .decode_to_string_list(candidate_k_itemset))

                    # If itemset satisfying minimum support, then it's a frequent itemset.
                    if self.support(decoded_candidate_k_itemset) >= self.__min_sup:
                        # Encode itemset to minimize memory usage.
                        (self
                         .__frequent_k_itemset[k]
                         .add(self.__itemset_encoder.encode_from_list(candidate_k_itemset)))

        # Frequent k-itemset cached result.
        return [self
                .__item_encoder
                .decode_to_string_list(self.__itemset_encoder.decode_to_list(k_itemset))
                for k_itemset in self.__frequent_k_itemset[k]]

    def frequent_itemset(self, len_descend=True):
        """Frequent itemset of the transactions.

        Calculate frequent k-itemset, k=1, ..., self.max_k,
        and combine result to form frequent itemset.

        Args:
            len_descend (bool):
                Show frequent itemset list in descend length order.

        Returns:
            list of frequent itemset:
                All frequent itemsets of the transactions.
        """

        f_itemset = []
        for k in range(self.__max_k):
            f_itemset = f_itemset + self.frequent_k_itemset(k+1)
        f_itemset.sort(key=len, reverse=len_descend)
        return f_itemset

    def association_rules(self):
        """List all association rules of the transactions.

        Split frequent itemset into two part, and calculate confidence.
        Number of possible conbination of split is Stiring number of second kind.

        Returns:
            list of dict:
                Each dict has two keys,
                'condition' stands occurence of itemset,
                'prediction' stands cooccurence itemset.
        """

        # If already calculated before, skip the calculation process.
        if self.__association_rules:
            pass
        # Else enumerate frequent itemset, split into two part and calculate confidence.
        else:
            for f_itemset in self.frequent_itemset():
                if len(f_itemset) >= 2:
                    for front, back in AssociationRuleMining.__split_itemset(f_itemset):
                        # If front -> back satisfying minimum confidence,
                        # then it's an association rule.
                        if self.confidence(front, back) >= self.__min_cof:
                            (self
                             .__association_rules
                             .append({'condition': front, 'prediction': back}))
                        # If back -> front satisfying minimum confidence,
                        # then it's an association rule.
                        if self.confidence(back, front) >= self.__min_cof:
                            (self
                             .__association_rules
                             .append({'condition': back, 'prediction': front}))

        # Association rule cached result.
        return self.__association_rules

# Test section.
if __name__ == '__main__':
    import json
    import os
    # Load data.
    DATA_PATH = os.path.dirname(os.path.abspath(__file__)) + '/data'
    DATA_NAME = '/example.json'

    with open(DATA_PATH + DATA_NAME, 'r') as f:
        # Create instance.
        ARM = AssociationRuleMining(transactions=json.loads(f.read()),
                                    min_sup=3/5,
                                    min_cof=0.5)

        # Print support count for all frequent itemsets.
        for fi in ARM.frequent_itemset():
            print('support count: {}, itemset: {}'.format(ARM.support_count(fi), fi))

        # Print confidence for all association rules.
        for rule in ARM.association_rules():
            print('confidence: {:.4f}, rule: {} -> {}'
                  .format(ARM.confidence(rule['condition'], rule['prediction']),
                          ''.join(rule['condition']),
                          ''.join(rule['prediction'])))
