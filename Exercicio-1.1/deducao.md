# Exercício 1.1 — Dedução da disponibilidade de um serviço replicado

## Parâmetros

- **n** – número de servidores (n > 0)
- **k** – número mínimo de servidores disponíveis necessário para o serviço ser acessado de forma consistente (0 < k ≤ n)
- **p** – probabilidade de cada servidor estar disponível em um dado instante (0 ≤ p ≤ 1)

## Modelo

Cada servidor é um experimento independente: disponível (probabilidade *p*) ou indisponível
(probabilidade *1 − p*). O número de servidores disponíveis *X* segue uma distribuição
**Binomial(n, p)**.

O serviço fica operacional quando **X ≥ k**, portanto:

```
disponibilidade A = P(X ≥ k)
```

---

## Caso k = 1 — operação de consulta (leitura)

O serviço está disponível quando **pelo menos 1** servidor está disponível.

Usamos o complemento: é mais fácil calcular a chance de **nenhum** servidor disponível.

- Probabilidade de 1 servidor estar indisponível: `1 − p`
- Probabilidade de **todos os n** estarem indisponíveis (independentes): `(1 − p)ⁿ`

Então:

```
A(k=1) = 1 − P(nenhum disponível)
A(k=1) = 1 − (1 − p)ⁿ
```

Verificação:
- p = 1  →  A = 1 − 0ⁿ = 1  (sempre disponível) ✓
- p = 0  →  A = 1 − 1ⁿ = 0  (nunca disponível) ✓
- Quanto maior n, maior A (mais réplicas = mais chances de ao menos uma estar de pé) ✓

---

## Caso k = n — operação de atualização (escrita)

O serviço está disponível quando **todos os n** servidores estão disponíveis
(se qualquer um falhar, a escrita pode ficar inconsistente).

- Probabilidade de 1 servidor estar disponível: `p`
- Probabilidade de **todos os n** estarem disponíveis (independentes): `pⁿ`

Então:

```
A(k=n) = pⁿ
```

Verificação:
- p = 1  →  A = 1ⁿ = 1  (sempre disponível) ✓
- p = 0  →  A = 0ⁿ = 0  (nunca disponível) ✓
- p = 0.9, n = 3  →  A = 0.9³ = 0.729  (72.9%)
- Quanto maior n, menor A (exigir mais réplicas de pé reduz a disponibilidade — contraste com o caso de leitura) ✓

---

## Caso geral — k genérico (0 < k ≤ n)

O serviço está disponível quando **X ≥ k**, onde X é o número de servidores disponíveis.
Somamos as probabilidades de todos os cenários que funcionam (i = k até i = n servidores de pé):

```
A = P(X=k) + P(X=k+1) + ... + P(X=n)
```

Cada termo `P(X=i)` vem da **distribuição binomial**: escolher **quais** i dos n servidores estão de pé
(combinação `C(n,i)`), cada um com probabilidade `p`, e os demais `n−i` caídos `(1−p)`:

```
P(X=i) = C(n,i) · pⁱ · (1−p)ⁿ⁻ⁱ
```

Então a fórmula geral:

```
                n
A(k)  =   Σ    C(n,i) · pⁱ · (1−p)ⁿ⁻ⁱ
              i=k
```

Note que ela **contém os dois casos anteriores**:
- k = 1  →  soma todos os termos exceto i=0  →  A = 1 − (1−p)ⁿ ✓
- k = n  →  sobra apenas i=n  →  A = pⁿ ✓