# Cache Simulator
A Python-based cache simulator that models separate instruction and data L1 caches with a unified L2 cache. It reports cache accesses, hits, misses, miss types, and hit/miss ratios.

## Features

- Separate instruction L1 and data L1 caches
- Unified L2 cache
- Configurable number of sets, block size, and associativity
- Compulsory and non-compulsory miss tracking
- Binary 32-bit memory address input
- Cache statistics and hit/miss ratios

## Usage

Run with the default cache configuration (64:4:1):

```bash
python cache_sim.py example_inputfilename.txt
```

Configure the L1 caches:

```bash
python cache_sim.py il1_params dl1_params inputfilename.txt
```

Configure all cache levels:

```bash
python cache_sim.py il1_params dl1_params l2_params inputfilename.txt
```

Cache parameters use the following format:

```text
number_of_sets:block_size:associativity
```

For example, `64:4:1` creates a cache with:

- 64 sets
- 4-byte blocks
- 1-way associativity

## Input Format

The input file must contain one 32-bit unsigned memory address per line, represented as a binary number:

```text
00000000000000000000000000000000
00000000000000000000000000000100
00000000000000000000000000001000
```

Addresses below 512MB are treated as data accesses; all other addresses are treated as instruction accesses.

The sample input is available in [`example_input.txt`](example_input.txt).

## Output

The simulator reports statistics for:

- Instruction L1 cache
- Data L1 cache
- Unified L2 cache
- Overall cache performance

Each report includes:

- Total accesses
- Hits
- Misses
- Compulsory misses
- Non-compulsory misses
- Hit ratio
- Miss ratio

## License

This project is licensed under the [MIT License](https://mit-license.org/). See the LICENSE file for details.
