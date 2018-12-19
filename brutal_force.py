import json
import os
import time
from encoder import StringToIntegerEncoder, ListToIntegerEncoder

class AssociationRuleMining:
    def __init__(self, transactions=None, min_sup=0.1, min_cof=0.1, max_k=0):
        self.__min_sup = min_sup
        self.__min_cof = min_cof
        self.__sup_count = {}
        self.__frequent_k_itemset = {}
        self.__association_rules = []
        self.__item_encoder = StringToIntegerEncoder()
        self.__itemset_encoder = ListToIntegerEncoder()
        self.__transactions = transactions
        self.__encoded_transactions = self.__item_encoder.encode_from_list_of_string_list(transactions)
        self.__n_transactions = len(transactions)
        self.__max_k = max_k
        if self.__max_k <= 0:
            for transaction in self.__transactions:
                if self.__max_k < len(transaction):
                    self.__max_k = len(transaction)

    @staticmethod
    def __enumerate_k_itemset(transaction, k=0):
        """Enumerate k-itemset in a transaction.

        Using back tracking algorithm to enumerate all combination of k-itemset.
        This method is entended to be private.

        Args:
            transaction (list of item): Target to be enumerated, item can be either encoded or decoded.
            k (int): Size of itemset.

        Returns:
            list of k-itemset: all k-itemset will be in list form.
        """
        all_k_itemset = []
        # Recursive end condition.
        if k > len(transaction):
            pass
        elif k == 1:
            for item in transaction:
                all_k_itemset.append([item])
        else:
            for i in range(len(transaction)):
                for k_1_itemset in AssociationRuleMining.__enumerate_k_itemset(transaction[i+1:], k-1):
                    k_itemset = [transaction[i]] + k_1_itemset
                    all_k_itemset.append(k_itemset)
        return all_k_itemset

    @staticmethod
    def __split_itemset(itemset):
        if len(itemset) == 2:
            return [([itemset[0]], [itemset[1]])]

        all_split = []
        all_split.append(([itemset[0]], itemset[1:]))
        for front, back in AssociationRuleMining.__split_itemset(itemset[1:]):
            new_split1 = ([itemset[0]]+front, back)
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
            itemset (list of item): Item cannot be encoded form.

        Returns:
            int: Support count for the given itemset.
        """
        itemset = self.__item_encoder.encode_from_string_list(itemset)
        encoded_itemset = self.__itemset_encoder.encode_from_list(itemset)
        if encoded_itemset in self.__sup_count:
            return self.__sup_count[encoded_itemset]
        else:
            self.__sup_count[encoded_itemset] = 0
            for transaction in self.__encoded_transactions:
                if all(map(lambda item: item in transaction, itemset)):
                    self.__sup_count[encoded_itemset] = self.__sup_count[encoded_itemset] + 1
            return self.__sup_count[encoded_itemset]

    def support(self, itemset):
        """Support for the itemset.

        Calculate the ratio of itemset appeared in all transaction.
        If itemset is already encoded before input,
        it will be given a zero support as return.

        Args:
            itemset (list of item): Item cannot be encoded form.

        Returns:
            int: Support for the given itemset.
        """
        return self.support_count(itemset) / self.__n_transactions

    def confidence(self, itemsetA, itemsetB):
        """Confidence of association rule itemsetA -> imtemsetB.

        If itemsetA or itemsetB is already encoded before input,
        it will be given a zero confidence as return.

        Args:
            itemsetA (list of item): when itemsetA appeared in a new transaction,
        """
        return self.support_count(itemsetA + itemsetB) / self.support_count(itemsetA)

    def frequent_k_itemset(self, k=1):
        # Error handler.
        if k <= 0:
            raise ValueError('k should be greater than 0.')
        if k > self.__max_k:
            raise ValueError('k should be smaller than or equal to max_k={}.'.format(self.__max_k))

        # Get frequent k-itemset from previous cahced computation result.
        if k in self.__frequent_k_itemset:
            pass
        else:
            # Compute.
            self.__frequent_k_itemset[k] = set()
            for transaction in self.__encoded_transactions:
                for k_itemset in AssociationRuleMining.__enumerate_k_itemset(transaction, k):
                    decoded_k_itemset = self.__item_encoder.decode_to_string_list(k_itemset)
                    if self.support(decoded_k_itemset) >= self.__min_sup:
                        self.__frequent_k_itemset[k].add(self.__itemset_encoder.encode_from_list(k_itemset))

        return [self.__item_encoder.decode_to_string_list(self.__itemset_encoder.decode_to_list(k_itemset))
            for k_itemset in self.__frequent_k_itemset[k]]

    def frequent_itemset(self, len_descend=True):
        f_itemset = []
        for k in range(self.__max_k):
            f_itemset = f_itemset + self.frequent_k_itemset(k+1)
        f_itemset.sort(key=lambda x: len(x), reverse=len_descend)
        return f_itemset

    def association_rules(self):
        if self.__association_rules:
            pass
        else:
            for f_itemset in self.frequent_itemset():
                if len(f_itemset) >= 2:
                    for front, back in AssociationRuleMining.__split_itemset(f_itemset):
                        if self.confidence(front, back) >= self.__min_cof:
                            self.__association_rules.append({'condition': front, 'prediction': back})
                        if self.confidence(back, front) >= self.__min_cof:
                            self.__association_rules.append({'condition': back, 'prediction': front})
        return self.__association_rules


if __name__ == '__main__':
    # Association rule mining settings.
    min_sup = 3/8
    min_cof = 0.5

    # Load data.
    data_path = os.path.dirname(os.path.abspath(__file__)) + '/data'
    # data_name = '/IBM.json'
    data_name = '/IBM.json'

    f = open(data_path + data_name, 'r')
    transactions = json.loads(f.read())
    f.close()

    arm = AssociationRuleMining(transactions=transactions, min_sup=min_sup, min_cof=min_cof)
    for f_itemset in arm.frequent_itemset():
        print('support count: {}, itemset: {}'.format(arm.support_count(f_itemset), f_itemset))

    for rule in arm.association_rules():
        print('confidence: {:.4f}, rule: {} -> {}'.format(arm.confidence(rule['condition'], rule['prediction']), ''.join(rule['condition']), ''.join(rule['prediction'])))