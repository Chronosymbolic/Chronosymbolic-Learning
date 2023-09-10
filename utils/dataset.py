from ordered_set import OrderedSet
from horndb.horndb import HornRelation


class Dataset:
    def __init__(self, logger, params, name='positive'):
        self._data = {}  # rel[fdecl]: set(dp's[tuples])
        self.logger = logger
        self.name = name
        self._rels = OrderedSet()  # HornRelations
        self._updated_rels = OrderedSet()  # HornRelations
        self._size = 0
        self._dup_count = 0
        self.params = params
        if self.name == 'positive':
            self.queue_mode = self.params['Dataset']['QueueModePos']
            self.queue_len = self.params['Dataset']['QueueLenPos']
        else:
            self.queue_mode = self.params['Dataset']['QueueModeNeg']
            self.queue_len = self.params['Dataset']['QueueLenNeg']


    def add_dp(self, rel, dp: list):
        """
        Input: rel (HornRelation), dp)
        Return True if it is not a duplicate dp
        """
        assert(isinstance(rel, HornRelation))
        self._rels.add(rel)
        self._updated_rels.add(rel)
        rel = rel.decl()
        if rel not in self._data.keys():
            self._data[rel] = OrderedSet()
        dp_size = len(self._data[rel])
        self._data[rel].add(tuple(dp))

        self.logger.debug(f'Add {self.name} DP {dp} for relation {rel.name()}')

        if len(self._data[rel]) != dp_size + 1:  # duplicate check
            self._dup_count += 1
            self.logger.debug(f'Duplicate data point {self._dup_count}')
            return False
        self._size += 1

        if self.queue_mode and len(self._data[rel]) > self.queue_len:  # fixed-len queue mode: FIFO
            poped_dp = self._data[rel].pop(0)
            self.logger.debug(f'Poped out {self.name} DP {poped_dp} for relation {rel.name()}')
            self._size -= 1
        return True

    def get_dps(self, rel=None):
        """Output a set of tuples"""
        assert(isinstance(rel, HornRelation))
        if rel is None:
            return self._data
        rel_decl = rel.decl()
        if rel_decl not in self._data.keys():
            return list()
        return list(self._data[rel_decl])

    def find_dp(self, rel, dp):
        """Return True if rel's dp in dataset"""
        assert(isinstance(rel, HornRelation))
        rel_dps = self.get_dps(rel)
        if tuple(dp) in rel_dps:
            return True
        return False

    def del_dp(self, rel, dp: list):
        """Return True if dp is deleted successfully"""
        assert(isinstance(rel, HornRelation))
        if rel not in self._data.keys():
            return False
        if dp not in self._data[rel]:
            return False
        self._data[rel].remove(dp)
        self._size -= 1
        return True

    def get_rels_fdecl(self):
        """Return a list of fdecl"""
        return list(self._data.keys())

    def get_rels(self):
        """Return a list of HornRelations"""
        return self._rels

    def get_updated_rels(self):
        """Return a list of HornRelations"""
        return self._updated_rels
    
    def clear_updated_rels(self):
        """clear self._updated_rels"""
        self._updated_rels = OrderedSet()

    def clear(self, rel=None):
        """
        Clear the whole dataset if no parameter is passed
        otherwise clear certain rel's all dps
        """
        if rel is None:
            self.logger.debug(f'Clear {self.name} DP for ALL relation')
            self._data = {}
            self._rels = OrderedSet()
            self._size = 0
        elif rel not in self._rels:
            return
        else:
            assert(isinstance(rel, HornRelation))
            self.logger.debug(f'Clear {self.name} DP for relation {rel.name()}')
            self._updated_rels.add(rel)
            self._rels.remove(rel)
            rel_decl = rel.decl()
            self._size -= len(self._data[rel_decl])
            self._data.pop(rel_decl, 0)

    def is_empty(self, rel=None):
        if rel is None:
            return len(self._data) <= 0
        assert(isinstance(rel, HornRelation))
        return rel.decl() not in self._data.keys() or len(self._data[rel.decl()]) <= 0

    def size(self, rel=None):
        if rel is None:
            return self._size
        assert(isinstance(rel, HornRelation))
        if rel.decl() not in self._data.keys():
            return 0
        return len(self._data[rel.decl()])

    def __str__(self) -> str:
        info = f'{self.name} dataset:\n'
        for k, v in self._data.items():
            info += f'Rel: {k}, dps: {v}\n'
        info += f'size: {self._size}'
        return info


class Dataset_v2:
    def __init__(self, logger, params, name='positive'):
        self._data = {}  # rel[fdecl]: set(dp's[tuples])
        self._tentative_data = {}  # rel[fdecl]: set(dp's[tuples])
        self._history_data = {}  # rel[fdecl]: set(dp's[tuples])
        self.logger = logger
        self.name = name
        self._rels = OrderedSet()  # HornRelations
        self._updated_rels = OrderedSet()  # HornRelations
        self._size = 0
        self._tentative_size = 0
        self._dup_count = 0
        self.params = params
        if self.name == 'positive':
            self.queue_mode = self.params['Dataset']['QueueModePos']
            self.queue_len = self.params['Dataset']['QueueLenPos']
        else:
            self.queue_mode = self.params['Dataset']['QueueModeNeg']
            self.queue_len = self.params['Dataset']['QueueLenNeg']
            self.tent_prop = self.params['Dataset']['QueueTentNegProp']
            self.real_prop =  self.params['Dataset']['QueueRealNegProp']


    def add_dp(self, rel, dp: list, is_tentative=False):
        """Input: rel (HornRelation), dp)
           Return True if it is not a duplicate dp"""
        assert(isinstance(rel, HornRelation))
        self._rels.add(rel)
        self._updated_rels.add(rel)
        rel = rel.decl()
        
        if is_tentative:
            if rel not in self._tentative_data.keys():
                self._tentative_data[rel] = OrderedSet()
            dp_size = len(self._tentative_data[rel])
            if rel in self._data.keys() and tuple(dp) in self._data[rel]:
                return True
            self._tentative_data[rel].add(tuple(dp))
            if len(self._tentative_data[rel]) != dp_size + 1:  # duplicate check
                self._dup_count += 1
                self.logger.debug(f'Duplicate tentative data point {self._dup_count}')
                return False
            self._tentative_size += 1
        else:
            if rel not in self._data.keys():
                self._data[rel] = OrderedSet()
            dp_size = len(self._data[rel])
            self._data[rel].add(tuple(dp))
            if len(self._data[rel]) != dp_size + 1:  # duplicate check
                self._dup_count += 1
                self.logger.debug(f'Duplicate data point {self._dup_count}')
                return False
            self._size += 1

        self.logger.debug(f'Add (tentative: {is_tentative}) {self.name} DP {dp} for relation {rel.name()}')

        if self.queue_mode:  # fixed-len queue mode: FIFO
            if not is_tentative and len(self._data[rel]) > int(self.real_prop * self.queue_len):
                poped_dp = self._data[rel].pop(0)
                self.logger.debug(f'Poped out {self.name} DP {poped_dp} for relation {rel.name()}')
                self._size -= 1

                if rel not in self._history_data.keys():
                    self._history_data[rel] = OrderedSet()
                self._history_data[rel].add(poped_dp)

            if is_tentative and len(self._tentative_data[rel]) > int(self.tent_prop * self.queue_len):
                poped_dp = self._tentative_data[rel].pop(0)
                self.logger.debug(f'Poped out {self.name} DP {poped_dp} for relation {rel.name()}')
                self._tentative_size -= 1
        return True

    def get_dps(self, rel):
        """Output a set of tuples"""
        assert(isinstance(rel, HornRelation))
        # if rel is None:
        #     return self._data
        rel_decl = rel.decl()
        if rel_decl not in self._data.keys() and rel_decl not in self._tentative_data.keys():
            return list()
        elif rel_decl not in self._data.keys():
            return list(self._tentative_data[rel_decl])
        elif rel_decl not in self._tentative_data.keys():
            return list(self._data[rel_decl])
        return list(self._data[rel_decl]) + list(self._tentative_data[rel_decl])

    def find_dp(self, rel, dp, exclude_tentative=False, exclude_history=True):
        """Return True if rel's dp in dataset"""
        assert(isinstance(rel, HornRelation))
        exclude_history = True if not self.queue_mode else exclude_history
        if exclude_tentative:
            rel_decl = rel.decl()
            if rel_decl not in self._data.keys():
                return False
            if tuple(dp) in self._data[rel_decl]:
                return True
            return False

        rel_dps = self.get_dps(rel)
        if tuple(dp) in rel_dps:
            return True
        if not exclude_history:
            rel_decl = rel.decl()
            if rel_decl not in self._history_data.keys():
                return False
            elif tuple(dp) in self._history_data[rel_decl]:
                return True
        return False

    def del_dp(self, rel, dp: list):
        """
        Return True if dp is deleted successfully
        Can only delete tentative ones
        """
        assert(isinstance(rel, HornRelation))
        if rel not in self._tentative_data.keys():
            return False
        if dp not in self._tentative_data[rel]:
            return False
        self._updated_rels.add(rel)
        self._tentative_data[rel].remove(dp)
        self._tentative_size -= 1
        return True

    def get_rels_fdecl(self):
        """Return a list of fdecl"""
        return [r.decl() for r in self._rels]

    def get_rels(self):
        """Return a list of HornRelations"""
        return self._rels
    
    def get_updated_rels(self):
        """Return a list of HornRelations"""
        return self._updated_rels
    
    def clear_updated_rels(self):
        """clear self._updated_rels"""
        self._updated_rels = OrderedSet()

    def clear(self, rel=None):
        """
        Clear the whole tentative dataset if no parameter is passed
        otherwise clear certain rel's all dps
        """
        if rel is None:
            self.logger.debug(f'Clear tentative {self.name} DP for ALL relation')
            self._tentative_data = {}
            self._tentative_size = 0
        elif rel.decl() not in self._tentative_data.keys():
            return
        else:
            assert(isinstance(rel, HornRelation))
            self.logger.debug(f'Clear tentative {self.name} DP for relation {rel.name()}')
            rel_decl = rel.decl()
            self._updated_rels.add(rel)
            self._tentative_size -= len(self._tentative_data[rel_decl])
            self._tentative_data.pop(rel_decl, 0)

    def is_empty(self, rel=None):
        if rel is None:
            return len(self._data) <= 0
        assert(isinstance(rel, HornRelation))
        if rel.decl() not in self._data.keys() and rel.decl() not in self._tentative_data.keys():
            return True
        elif rel.decl() not in self._tentative_data.keys():
            return len(self._data[rel.decl()]) <= 0
        elif rel.decl() not in self._data.keys():
            return len(self._tentative_data[rel.decl()]) <= 0
        return len(self._tentative_data[rel.decl()]) + len(self._data[rel.decl()]) <= 0

    def size(self, rel=None):
        if rel is None:
            return self._size + self._tentative_size
        assert(isinstance(rel, HornRelation))
        if self.is_empty(rel):
            return 0
        if rel.decl() not in self._data.keys():
            return len(self._tentative_data[rel.decl()])
        if rel.decl() not in self._tentative_data.keys():
            return len(self._data[rel.decl()])
        return len(self._data[rel.decl()]) + len(self._tentative_data[rel.decl()])

    def __str__(self) -> str:
        info = f'{self.name} dataset:\n'
        for k, v in self._data.items():
            info += f'Rel: {k}, dps: {v}\n'
        info += f'{self.name} tentative dataset:\n'
        for k, v in self._tentative_data.items():
            info += f'Rel: {k}, dps: {v}\n'
        info += f'size: {self._size}, tentative_size: {self._tentative_size}'
        return info
