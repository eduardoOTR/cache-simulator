import math
from pathlib import Path

class Cache:
    def __init__(self, n_sets, b_size, assoc):
        self.n_sets = n_sets
        self.b_size = b_size
        self.assoc = assoc
        self.hits = 0
        self.misses = 0
        self.acessos = 0
        self.vals = [[0 for _ in range(assoc)] for _ in range(n_sets // assoc)]
        self.tags = [["" for _ in range(assoc)] for _ in range(n_sets // assoc)]
        self.offset = int(math.log(b_size, 2))
        self.indice = int(math.log(n_sets // assoc, 2))
        self.tag = 32 - self.offset - self.indice

    def acesso(self, endereco):
        self.acessos += 1
        endereco = int(endereco, 2)
        tag_bin = bin(endereco >> (self.offset + self.indice))
        indice_num = (endereco >> self.offset) & (int(math.pow(2, self.indice)) - 1)
        print(tag_bin)
        print(indice_num)

        if self.vals[indice_num][0] == 1:
            if self.tags[indice_num][0] == tag_bin:
                self.hits += 1
            else:
                self.misses += 1
                self.tags[indice_num][0] = tag_bin
        else:
            self.misses += 1
            self.vals[indice_num][0] = 1
            self.tags[indice_num][0] = tag_bin

    def status(self):
        print(f"Hits: {self.hits} | Misses: {self.misses} | Acessos: {self.acessos}")


n_sets, b_size, assoc = map(int, input("Digite a configuração da il1 (n_sets b_size assoc): ").split())

il1 = Cache(n_sets, b_size, assoc)

pasta_atual = Path(__file__).resolve().parent
caminho_do_txt = pasta_atual / "entrada.txt"

with open(caminho_do_txt, "r", encoding="utf-8") as entrada:
    for linha in entrada:
        endereco = linha.strip()
        il1.acesso(endereco)

il1.status()