import sys
import math
from collections import deque

if len(sys.argv) == 5:
    filename = sys.argv[1]
    no_processors = int(sys.argv[2])
    cache_size = int(sys.argv[3])
    cache_block_size = int(sys.argv[4])
else:
    filename = "WEATHER"
    no_processors = 4
    cache_size = 4096
    cache_block_size = 64

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
cache_access_indie = []
cache_miss_indie = []
for x in range(no_processors):
    cache_miss_indie.append(0)
    cache_access_indie.append(0)
#opening files
files = []
for x in range(no_processors):
    files.append(open('dump/weather' + str(no_processors) + '/' + filename + str(x + 1) + '.PRG', 'r'))

#initialisation of cache
cache = []
for x in range(no_processors):
    cache.append([])
    i = 0
    while i < cache_blocks:
        cache[x].append(['I',0])
        i += 1

#initialisation of buses
bus = []
for x in range(no_processors):
    bus.append(deque([]))

#initialisation of stall variables
stall = []
for x in range(no_processors):
    stall.append(0)

#load mem access line into buffer
line = []
for x in range(no_processors):
    line.append(files[x].readline())
#start main processing
completed = False
count = 0
while not completed:
    for x in range(no_processors):
        inst_read = False
        data_read = False
        #clear bus
        while bus[x]:
            op, index, tag = bus[x].popleft()
            if cache[x][index][1] == tag:
                if op == 'r':
                    cache[x][index][0] = 'S'
                elif op == 'w':
                    cache[x][index][0] = 'I'
        #process line/s else, stall and minus 1 from CPU cycle
        if stall[x] == 0:
            for y in range(2):
                if line[x]:
                    inst_type = line[x][0]
                    inst_memory = line[x][2:]
                    if inst_type == '0':
                        if not inst_read:
                            inst_read = True
                        else:
                            break
                    elif inst_type == '2' or inst_type == '3':
                        if data_read:
                            break
                        else:
                            data_read = True
                            cache_access += 1
                            cache_access_indie[x] += 1
                            memory_block_number = bin(int(inst_memory, 16))[2:].zfill(32)
                            tag_index = memory_block_number[:-memory_block_offset]
                            cache_index = tag_index[-cache_block_offset:]
                            tag = tag_index[:-cache_block_offset]
                            #start of cache lookup
                            int_cache_index = int(cache_index,2)
                            int_tag = int(tag, 2)
                            if cache[x][int_cache_index][1] != int_tag or cache[x][int_cache_index][0] == 'I':
                                cache_miss += 1
                                cache_miss_indie[x] += 1
                                stall[x] = 10
                                for z in range(no_processors):
                                    if z != x and cache[y][int_cache_index][1] == int_tag:
                                        if cache[z][int_cache_index][0] == 'M':
                                            cache[z][int_cache_index][0] = 'E'
                                break
                            elif inst_type == '2':
                                pass
                            elif inst_type == '3':
                                cache[x][int_cache_index][0] = 'M'
                                for z in range(no_processors):
                                    tmp = 'w', int_cache_index, int_tag
                                    if x != z:
                                        bus[y].append(tmp)
                    line[x] = files[x].readline()
        else:
            stall[x] -= 1
            while bus[x]:
                op, index, tag = bus[x].popleft()
                if cache[x][index][1] == tag:
                    if op == 'r':
                        cache[x][index][0] = 'S'
                    elif op == 'w':
                        cache[x][index][0] = 'I'
            if stall[x] == 0:
                inst_type = line[x][0]
                inst_memory = line[x][2:]
                memory_block_number = bin(int(inst_memory, 16))[2:].zfill(32)
                tag_index = memory_block_number[:-memory_block_offset]
                cache_index = tag_index[-cache_block_offset:]
                tag = tag_index[:-cache_block_offset]
                #start of cache lookup
                int_cache_index = int(cache_index,2)
                int_tag = int(tag, 2)
                if inst_type == '3':
                    cache[x][int_cache_index][0] = 'M'
                    cache[x][int_cache_index][1] = int_tag
                    for y in range(no_processors):
                        tmp = 'w', int_cache_index, int_tag
                        if x != y:
                            bus[y].append(tmp)
                elif inst_type == '2':
                    state = 'E'
                    for y in range(no_processors):
                        if x != y and cache[y][int_cache_index][1] == int_tag:
                            state = 'S'
                            break
                    cache[x][int_cache_index][0] = state
                    cache[x][int_cache_index][1] = int_tag 
                line[x] = files[x].readline()
    #stops when all processor files are done checking
    completed = True
    for x in range(no_processors):
        if line[x]:
            completed = False


for x in range(no_processors):
    print "Processor " + str(x + 1)
    print "Cache Miss       = " + str(cache_miss_indie[x]) 
    print "Cache Access     = " + str(cache_access_indie[x]) 
    print "Cache Miss Ratio = " +  str(cache_miss_indie[x]/float(cache_access_indie[x]))
    print ""

