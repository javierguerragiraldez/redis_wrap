
from redis_systems import *

class ListFu (redis_obj):

    def append(self, item):
        self.conn.rpush(self.name, item)

    def extend(self, iterable):
        for item in iterable:
            self.append(item)

    def remove(self, value):
        self.conn.lrem(self.name, value)

    def pop(self, index=None):
        if index:
            raise ValueError('Not supported')
        return self.conn.rpop(self.name)

    def list_trim(self, start, stop):
        self.conn.ltrim(self.name, start, stop)

    def __len__(self):
        return self.conn.llen(self.name)

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = key.start
            if start == None: start = 0
            stop = key.stop
            if stop == None: stop = -1
            return self.conn.lrange(self.name, start, stop)

        val = self.conn.lindex(self.name, key)
        if not val:
            raise IndexError
        return val

    def __setitem__(self, key, value):
        try:
            self.conn.lset(self.name, key, value)
        except redis.exceptions.ResponseError:
            raise IndexError

    def __iter__(self):
        i = 0
        while True:
            items = self.conn.lrange(self.name, i, i+30)
            if len(items) == 0:
                raise StopIteration
            for item in items:
                yield item
            i += 30

    def __iadd__(self, other):
        self.conn.rpush(self.name, *other)
        return self

    def __add__(self, other):
        nl = ListFu('_oper_add-%s-%s'%(self.name, other.name),
            self.system, persistent=False)
        nl += self
        nl += other
        return nl
