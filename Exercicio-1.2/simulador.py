import pathlib
import random

import matplotlib.pyplot as plt
import pandas as pd

from analitico import disponibilidade

BASE_DIR = pathlib.Path(__file__).resolve().parent


def simular_rodada(n, p, rng):
    """Simula UMA rodada: sorteia o estado de cada servidor.

    Para cada servidor gera um número aleatório em [0, 1]; se for
    <= p consideramos o servidor disponível. Retorna a contagem de
    servidores disponíveis.
    """
    disponiveis = 0
    for _ in range(n):
        u = rng.random()
        if u <= p:
            disponiveis += 1
    return disponiveis


def simular(n, k, p, rodadas=100000, rng=None):
    """Frequência experimental de disponibilidade via simulação."""
    if rng is None:
        rng = random.Random()
    sucessos = 0
    for _ in range(rodadas):
        if simular_rodada(n, p, rng) >= k:
            sucessos += 1
    return sucessos / rodadas


if __name__ == "__main__":
    rng = random.Random(42)  # semente fixa -> resultados reproduzíveis

    test = simular_rodada(3, 0.5, rng)
    print(f"Teste: uma rodada (n=3, p=0.5) -> {test} disponíveis")

    valores_n = [1, 2, 3, 5, 10]
    valores_p = [0.7, 0.85, 0.95, 0.99]
    N_RODADAS = 100000

    linhas = []
    for n in valores_n:
        ks = {1: "k=1", max(1, n // 2): "k=n/2", n: "k=n"}
        for k, rotulo in sorted(ks.items()):
            for p in valores_p:
                analitico = disponibilidade(n, k, p)
                empirico = simular(n, k, p, N_RODADAS, rng)
                linhas.append({
                    "n": n,
                    "k": k,
                    "criterio": rotulo,
                    "p": p,
                    "analitico": round(analitico, 6),
                    "simulado": round(empirico, 6),
                    "diferenca": round(abs(analitico - empirico), 6),
                })

    tabela = pd.DataFrame(linhas)
    tabela.to_csv(BASE_DIR / "tabela_simulacao.csv", index=False)
    print(tabela.to_string(index=False))

    print("\nGerando gráficos 2D (analítico x simulado)...")
    p_axis = [i / 100 for i in range(50, 101)]
    criterios = ["k=1", "k=n/2", "k=n"]

    for criterio in criterios:
        plt.figure()
        for n in valores_n:
            k = {"k=1": 1, "k=n/2": max(1, n // 2), "k=n": n}[criterio]
            series_ana = [disponibilidade(n, k, p) for p in p_axis]
            series_sim = [simular(n, k, p, N_RODADAS, rng) for p in p_axis]
            plt.plot(p_axis, series_ana, marker="o", label=f"analítico n={n}", linestyle="-")
            plt.plot(p_axis, series_sim, marker="x", label=f"simulado n={n}", linestyle="--")
        plt.title(f"Disponibilidade analítica x simulada — {criterio}")
        plt.xlabel("p (probabilidade por servidor)")
        plt.ylabel("A (disponibilidade do serviço)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        fig_name = f"grafico_simulacao_{criterio.replace('/', '_')}.png"
        plt.savefig(BASE_DIR / fig_name)
        print(f"  salvo: {fig_name}")