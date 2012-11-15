import math
import threading
from collections import deque

class ThreadWrapper(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
 
    def run(self):
        self._target(*self._args)

bus_mutex = []
print_mutex = threading.Lock()

bus = []

def init(no_processors):
    for i in range(no_processors):
        bus_mutex.append(threading.Lock())
        bus.append(deque([]))

def process_file(filename, no_processors, cache_size, cache_block_size, thread_no):
    print filename + " " + str(no_processors) + " " + str(cache_size) + " " + str(cache_block_size) + " " + str(thread_no)
    if thread_no != 0:
        return "b"
    #initialisation of variables
    cache_blocks = cache_size / cache_block_size
    cache_block_offset = int(math.log(cache_blocks, 2))
    word_size_in_bits = 16
    word_size = word_size_in_bits / 8
    memory_address_size_in_bits = 32
    memory_address_size = memory_address_size_in_bits / 8
    memory_block_offset = int(math.log(cache_block_size, 2))
    tag_size = memory_address_size_in_bits - memory_block_offset - cache_block_offset
    #analytics variables
    cycle_count = 0
    cache_access = 0
    cache_miss = 0

    file = open('dump/weather' + str(no_processors) + '/' + filename + str(thread_no + 1) + '.PRG', 'r')
    print 'dump/weather' + str(no_processors) + '/' + filename + str(thread_no + 1) + '.PRG'
    #initialisation of cache
    i = 0
    cache = []
    while i < cache_blocks:
        cache.append([0,0])
        i += 1
    line = file.readline()
    inst_read = False
    data_read = False
    while line:
        if i % 100000 == 0:
            print i
        i += 1
        inst_type = line[0]
        inst_memory = line[2:]
        if inst_type == '0':
            if not inst_read:
                inst_read = True
            else:
                cycle_count += 1
                inst_read = False
        elif (inst_type == '2' or inst_type == '3'):
            if not data_read:
                data_read = True
            else:
                cycle_count += 1
                data_read = False
            memory_block_number = bin(int(inst_memory, 16))[2:].zfill(32)
            tag_index = memory_block_number[:-memory_block_offset]
            cache_index = tag_index[-cache_block_offset:]
            tag = tag_index[:-cache_block_offset]
            #start of cache lookup
            int_cache_index = int(cache_index,2)
            int_tag = int(tag, 2)
            cache_access += 1
            if cache[int_cache_index][1] == int_tag:

                if cache[int_cache_index][0] == 'M':
                    pass
                elif cache[int_cache_index][0] == 'E':
                    pass
                elif cache[int_cache_index][0] == 'S':
                    pass
                elif cache[int_cache_index][0] == 'I':
                    cache_miss += 1
                    cycle_count += 10
            else:
                cache_miss += 1
                cycle_count += 10
                cache[int_cache_index][0] = 'M'
                cache[int_cache_index][1] = int_tag
                if cache[int_cache_index][0] == 'M':
                    pass
                elif cache[int_cache_index][0] == 'E':
                    pass
                elif cache[int_cache_index][0] == 'S':
                    pass
                elif cache[int_cache_index][0] == 'I':
                    pass
        line = file.readline()
    
    print "Processor : " + str(thread_no + 1)
    print_mutex.acquire()
    print cache_miss
    print cache_access
    print cache_miss/float(cache_access)
    print_mutex.release()