import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analitico import disponibilidade

BASE_DIR = pathlib.Path(__file__).resolve().parent

# Bloco de rodadas processado de cada vez (evita estourar a memória
# quando n e o número de rodadas são grandes).
BLOCO = 100_000


def simular_rodada(n, p, rng):
    """Simula UMA rodada: sorteia o estado de cada servidor.

    Para cada servidor gera um número aleatório em [0, 1]; se for
    <= p consideramos o servidor disponível. Retorna a contagem de
    servidores disponíveis.
    """
    u = rng.random(n)
    return int((u <= p).sum())


def simular(n, k, p, rodadas=100000, rng=None):
    """Frequência experimental de disponibilidade via simulação.

    A simulação é vetorizada com numpy e processada em blocos de
    ``BLOCO`` rodadas, de modo que valores grandes de n e de rodadas
    continuam tratáveis.
    """
    if rng is None:
        rng = np.random.default_rng()
    sucessos = 0
    restantes = rodadas
    while restantes > 0:
        bloco = min(BLOCO, restantes)
        u = rng.random((bloco, n))
        disponiveis = (u <= p).sum(axis=1)
        sucessos += int((disponiveis >= k).sum())
        restantes -= bloco
    return sucessos / rodadas


if __name__ == "__main__":
    rng = np.random.default_rng(42)  # semente fixa -> resultados reproduzíveis

    test = simular_rodada(3, 0.5, rng)
    print(f"Teste: uma rodada (n=3, p=0.5) -> {test} disponíveis")

    valores_rodadas = [1, 100, 100000]
    valores_n = [10, 50, 100]
    valores_p = [0.7, 0.85, 0.95, 0.99]

    linhas = []
    for rodadas in valores_rodadas:
        for n in valores_n:
            ks = {1: "k=1", max(1, n // 2): "k=n/2", n: "k=n"}
            for k, rotulo in sorted(ks.items()):
                for p in valores_p:
                    analitico = disponibilidade(n, k, p)
                    empirico = simular(n, k, p, rodadas, rng)
                    linhas.append({
                        "rodadas": rodadas,
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

    for rodadas in valores_rodadas:
        trecho = tabela[tabela["rodadas"] == rodadas]
        print(f"\n=== Simulação com {rodadas} rodadas (n=100, k=n) ===")
        amostra = trecho[(trecho["n"] == 100) & (trecho["k"] == 100)]
        print(amostra.to_string(index=False))

    print("\nGerando gráficos 2D (analítico x simulado por nº de rodadas)...")
    p_axis = [round(v, 2) for v in np.linspace(0.0, 1.0, 21)]
    criterios = ["k=1", "k=n/2", "k=n"]

    for n in valores_n:
        fig, axes = plt.subplots(1, len(valores_rodadas), figsize=(22, 6),
                                 sharex=True, sharey=True)
        for ax, rodadas in zip(axes, valores_rodadas):
            for criterio in criterios:
                k = {"k=1": 1, "k=n/2": max(1, n // 2), "k=n": n}[criterio]
                series_ana = [disponibilidade(n, k, p) for p in p_axis]
                series_sim = [simular(n, k, p, rodadas, rng) for p in p_axis]
                ax.plot(p_axis, series_ana, marker="o", label=f"Analítico {criterio}", linestyle="-")
                ax.plot(p_axis, series_sim, marker="x", label=f"Simulado {criterio}", linestyle="--")
            rotulo_rodadas = f"{rodadas:,}".replace(",", ".")
            ax.set_xlim(-0.02, 1.18)
            ax.set_ylim(-0.02, 1.05)
            ax.grid(True, alpha=0.3)
            ax.legend(title=f"{rotulo_rodadas} rodadas", fontsize=8,
                      title_fontsize=9, loc="lower right")
        fig.suptitle(f"Disponibilidade analítica x simulada — n = {n}")
        fig.supxlabel("p (probabilidade por servidor)")
        fig.supylabel("A (disponibilidade do serviço)")
        plt.tight_layout()
        fig_name = f"grafico_simulacao_n={n}.png"
        fig.savefig(BASE_DIR / fig_name)
        print(f"  salvo: {fig_name}")
