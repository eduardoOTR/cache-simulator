import math
import random
import sys
from pathlib import Path

DEFAULT_IL1 = (64, 4, 1)
DEFAULT_DL1 = (64, 4, 1)
DEFAULT_L2  = (64, 4, 1)

DATA_LIMIT = 512 * 1024 * 1024

class Cache:
    def __init__(self, n_sets, b_size, assoc):
        self.n_sets = n_sets
        self.b_size = b_size
        self.assoc = assoc

        self.hits = 0
        self.misses = 0
        self.compulsory_misses = 0
        self.non_compulsory_misses = 0
        self.accesses = 0

        self.vals = [[0 for _ in range(assoc)] for _ in range(n_sets)]
        self.tags = [[-1 for _ in range(assoc)] for _ in range(n_sets)]

        self.offset = int(math.log(b_size, 2))
        self.index = int(math.log(n_sets, 2))
        #self.tag = 32 - self.offset - self.index

        self.seen_blocks = set()

    def access(self, address_int):
        self.accesses += 1

        block_address = address_int >> self.offset
        tag = block_address >> self.index if self.index > 0 else block_address
        index = block_address & ((1 << self.index) - 1) if self.index > 0 else 0

        #print(tag)
        #print(index)

        hit = False
        for i in range(self.assoc):
            if self.vals[index][i] == 1 and self.tags[index][i] == tag:
                hit = True
                break

        if hit:
            self.hits += 1
            return True
        else:
            self.misses += 1

            if block_address not in self.seen_blocks:
                self.compulsory_misses += 1
                self.seen_blocks.add(block_address)
            else:
                self.non_compulsory_misses += 1

            empty_way = -1
            for i in range(self.assoc):
                if self.vals[index][i] == 0:
                    empty_way = i
                    break
            
            if empty_way != -1:
                target_way = empty_way
            else:
                target_way = random.randint(0, self.assoc - 1)
            
            self.vals[index][target_way] = 1
            self.tags[index][target_way] = tag
            return False

    def status(self, name="Cache"):
        hit_ratio = (self.hits / self.accesses * 100) if self.accesses > 0 else 0
        miss_ratio = (self.misses / self.accesses * 100) if self.accesses > 0 else 0

        print(f"{name}:")
        print(f"Acesses: {self.accesses}")
        print(f"Hits: {self.hits}") 
        print(f"Misses: {self.misses}\nCompulsory misses: {self.compulsory_misses} | Non-compulsory (capacity/conflict) misses: {self.non_compulsory_misses}")
        print(f"Hit Ratio: {hit_ratio:.2f}%")
        print(f"Miss Ratio: {miss_ratio:.2f}%\n")

def print_global(il1, dl1, l2):
    total_accesses = il1.accesses + dl1.accesses
    total_hits = total_accesses - l2.misses

    print("Global Statistics:")
    print(f"Accesses: {total_accesses}")
    print(f"Hits: {total_hits}") 
    print(f"Misses: {l2.misses}\nCompulsory misses: {l2.compulsory_misses} | Non-compulsory (capacity/conflict) misses: {l2.non_compulsory_misses}")

    if total_accesses > 0:
        global_miss_ratio = (l2.misses / total_accesses) * 100
        global_hit_ratio = 100 - global_miss_ratio
        print(f"Hit Ratio: {global_hit_ratio:.2f}%")
        print(f"Miss Ratio: {global_miss_ratio:.2f}%\n")
    else:
        print("Hit Ratio: 0.00%")
        print("Miss Ratio: 0.00%\n")

def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

def parse_params(config, name):
    params = config.split(":")

    if len(params) != 3:
        raise ValueError(f"Invalid {name} configuration. Expected format: nsets:bsize:assoc")
    
    try:
        n_sets, b_size, assoc = map(int, params)
    except ValueError:
        raise ValueError(f"Invalid values in {name} configuration. All parameters must be integers.")

    if not is_power_of_two(n_sets):
        raise ValueError(f"{name} n_sets must be a power of 2.")
    if not is_power_of_two(b_size):
        raise ValueError(f"{name} b_size must be a power of 2.")
    if assoc <= 0:
        raise ValueError(f"{name} associativity must be positive.")

    return n_sets, b_size, assoc

def parse_arguments():
    arguments = sys.argv[1:]

    if len(arguments) == 1:
        il1_params = DEFAULT_IL1
        dl1_params = DEFAULT_DL1
        l2_params = DEFAULT_L2

        input_file = arguments[0]

    elif len(arguments) == 3:
        il1_params = parse_params(arguments[0], "iL1")
        dl1_params = parse_params(arguments[1], "dL1")
        l2_params = DEFAULT_L2

        input_file = arguments[2]

    elif len(arguments) == 4:
        il1_params = parse_params(arguments[0], "iL1")
        dl1_params = parse_params(arguments[1], "dL1")
        l2_params = parse_params(arguments[2], "L2")

        input_file = arguments[3]
    else:
        raise ValueError(
            "Invalid number of arguments.\n\n"
            "Expected formats:\n"
            "python cache_simulator.py inputfilename.txt\n"
            "python cache_simulator.py il1_params dl1_params inputfilename.txt\n"
            "python cache_simulator.py il1_params dl1_params l2_params inputfilename.txt\n\n"
            "OBS: Parameter example: 64:4:1"
        )
    
    return il1_params, dl1_params, l2_params, input_file

def main():
    try:
        il1_params, dl1_params, l2_params, input_file = parse_arguments()
    except ValueError as ve:
        print(f"Error: {ve}")
        return 1

    input_path = Path(input_file)

    if not input_path.is_file():
        print(f"Error: Input file not found: {input_path}")
        return 1

    il1 = Cache(*il1_params)
    dl1 = Cache(*dl1_params)
    l2 = Cache(*l2_params)

    try:
        with open(input_path, "r", encoding="utf-8") as input:
            for line in input:
                address = line.strip()
                if not address:
                    continue

                try:
                    address_int = int(address, 2)
                except ValueError:
                    print("Error: One of the lines could not be read because it was not a binary number.")
                    continue

                if address_int < 0 or address_int >= (1 << 32):
                    print("Error: Address must be a 32-bit unsigned integer.")
                    continue

                if address_int < DATA_LIMIT:
                    hit_dl1 = dl1.access(address_int)
                    if not hit_dl1:
                        l2.access(address_int)
                else:
                    hit_il1 = il1.access(address_int)
                    if not hit_il1:
                        l2.access(address_int)

        il1.status("\nInstruction L1 (iL1)")
        dl1.status("Data L1 (dL1)")
        l2.status("Unified L2")
        print_global(il1, dl1, l2)

    except OSError as error:
        print(f"Error reading input file: {error}")
        return 1

    return 0

sys.exit(main())