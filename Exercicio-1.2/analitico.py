import math
import os
import pathlib

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = pathlib.Path(__file__).resolve().parent


def combinacao(n, i):
    """Número de combinações C(n, i) = n! / (i! (n-i)!)."""
    return math.comb(n, i)


def disponibilidade(n, k, p):
    """
    Disponibilidade de um serviço replicado em n servidores.

    A = Soma (i = k até n) de C(n, i) * p^i * (1-p)^(n-i)

    Parâmetros:
        n: número de servidores (n > 0)
        k: mínimo de servidores disponíveis para o serviço funcionar (0 < k <= n)
        p: probabilidade de cada servidor estar disponível (0 <= p <= 1)
    """
    soma = 0.0
    for i in range(k, n + 1):
        soma += combinacao(n, i) * (p ** i) * ((1 - p) ** (n - i))
    return soma


if __name__ == "__main__":
    print("Testes da fórmula geral vs casos extremos:")

    n, p = 3, 0.9

    a_k1 = disponibilidade(n, 1, p)
    esperado_k1 = 1 - (1 - p) ** n
    print(f"k=1  -> formula geral: {a_k1:.4f} | esperado 1-(1-p)^n: {esperado_k1:.4f}")

    a_kn = disponibilidade(n, n, p)
    esperado_kn = p ** n
    print(f"k=n  -> formula geral: {a_kn:.4f} | esperado p^n:        {esperado_kn:.4f}")

    a_medio = disponibilidade(n, 2, p)
    esperado_medio = combinacao(3, 2) * p ** 2 * (1 - p) + combinacao(3, 3) * p ** 3
    print(f"k=2  -> formula geral: {a_medio:.4f} | calculo manual:     {esperado_medio:.4f}")

    print("\nTabela analítica: disponibilidade para n, k, p variados")

    valores_n = [1, 2, 3, 5, 10]
    valores_p = [0.7, 0.85, 0.95, 0.99]

    linhas = []
    for n in valores_n:
        ks = {1: "k=1", max(1, n // 2): "k=n/2", n: "k=n"}
        for k, rotulo in sorted(ks.items()):
            for p in valores_p:
                linhas.append({
                    "n": n,
                    "k": k,
                    "criterio": rotulo,
                    "p": p,
                    "disponibilidade": round(disponibilidade(n, k, p), 6),
                })

    tabela = pd.DataFrame(linhas)
    tabela.to_csv(BASE_DIR / "tabela_analitica.csv", index=False)
    print(tabela.to_string(index=False))

    print("\nGerando gráficos 2D...")
    p_axis = [round(i / 20, 2) for i in range(0, 21)]
    criterios = ["k=1", "k=n/2", "k=n"]

    for criterio in criterios:
        plt.figure(figsize=(10, 6))
        for n in valores_n:
            k = {"k=1": 1, "k=n/2": max(1, n // 2), "k=n": n}[criterio]
            series = [disponibilidade(n, k, p) for p in p_axis]
            plt.plot(p_axis, series, marker="o", label=f"n = {n}")
        plt.xlim(-0.02, 1.15)
        plt.ylim(-0.02, 1.05)
        plt.title(f"Disponibilidade analítica — {criterio}")
        plt.xlabel("p (probabilidade por servidor)")
        plt.ylabel("A (disponibilidade do serviço)")
        plt.grid(True, alpha=0.3)
        plt.legend(loc="lower right")
        plt.tight_layout()
        fig_name = f"grafico_analitico_{criterio.replace('/', '_')}.png"
        plt.savefig(BASE_DIR / fig_name)
        print(f"  salvo: {fig_name}")