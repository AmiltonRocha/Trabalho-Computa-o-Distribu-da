# Trabalho de Computação Distribuída — Disponibilidade de Serviços Replicados

**Autor:** Amilton Rocha Holanda
**Disciplina:** Computação Distribuída
**Data:** setembro/2026

---

Prof., este trabalho contém o desenvolvimento dos Exercícios 1.1 e 1.2 do
capítulo de replicação de dados: a dedução da fórmula de disponibilidade de um
serviço replicado e sua validação por cálculo analítico e por simulação
estocástica.

Antes de começar, quero deixar registrado que contei com o **auxílio de uma
ferramenta de IA** (assistente de programação) ao longo de todo o trabalho,
tanto na **escrita** (organização, revisão e redação do conteúdo) quanto na
**formação de algumas funções** em Python. Deixei notas específicas nos
trechos em que isso aconteceu. Todos os conceitos e resultados foram revisados
e validados por mim antes da entrega.

---

# Exercício 1.1 — Dedução da fórmula de disponibilidade

Nesta parte explico o raciocínio passo a passo de como cheguei à fórmula
matemática da disponibilidade de um serviço replicado em múltiplos servidores,
começando pelos casos extremos (k = 1 e k = n) e chegando à fórmula geral para
qualquer k.

## 1.1.1. Definição dos parâmetros

| Parâmetro | Significado | Domínio |
|-----------|-------------|---------|
| **n** | Número de servidores do serviço (réplicas) | n > 0 |
| **k** | Número mínimo de servidores disponíveis necessário para o serviço ser acessado de forma consistente | 0 < k ≤ n |
| **p** | Probabilidade de cada servidor estar disponível em um dado instante | 0 ≤ p ≤ 1 |

A disponibilidade **A** do serviço é a probabilidade de o serviço estar
operacional, ou seja, a probabilidade de ter **pelo menos k servidores
disponíveis** em um dado instante. (Nota: a organização desta seção contou
com auxílio de IA na revisão, mas o conteúdo conceitual foi por mim
compreendido e validado.)

## 1.1.2. Modelo probabilístico

Cada servidor é tratado como um experimento de Bernoulli independente:
- disponível, com probabilidade **p**
- indisponível, com probabilidade **1 − p**

Como temos **n** servidores independentes, o número **X** de servidores
disponíveis segue uma **distribuição Binomial(n, p)**. O serviço fica
operacional quando **X ≥ k**, portanto:

```
A = P(X ≥ k)
```

É exatamente essa probabilidade que queremos expressar em função de n, k e p.

## 1.1.3. Caso extremo: k = 1 (operação de consulta/leitura)

Quando k = 1, o serviço está disponível se **pelo menos um** servidor estiver
de pé. Nesse cenário, cai um servidor e outras réplicas continuam atendendo,
por isso é o modelo típico de **leitura/consulta**.

Para facilitar o cálculo, uso o **complemento**: em vez de calcular a
probabilidade de *ter pelo menos 1 disponível*, calculo a probabilidade de
*não ter nenhum disponível* e subtraio de 1.

- Probabilidade de **um** servidor estar indisponível: `1 − p`
- Como os servidores são independentes, a probabilidade de **todos os n**
  estarem indisponíveis é o produto:

```
P(nenhum disponível) = (1 − p)ⁿ
```

Logo:

```
A(k=1) = 1 − P(nenhum disponível)
A(k=1) = 1 − (1 − p)ⁿ
```

**Verificação da fórmula** (teste de sanidade):
- Se p = 1: `A = 1 − 0ⁿ = 1` → serviço sempre disponível ✓
- Se p = 0: `A = 1 − 1ⁿ = 0` → serviço nunca disponível ✓
- Aumentar **n** aumenta **A**: mais réplicas = mais chances de ao menos uma
  estar de pé. Faz sentido: replicação beneficia leitura.

## 1.1.4. Caso extremo: k = n (operação de atualização/escrita)

Quando k = n, o serviço só está disponível se **todos** os n servidores
estiverem disponíveis. Se qualquer servidor falhar, não dá para garantir a
consistência da operação, por isso k = n é o modelo típico de
**atualização/escrita** (regra de quórum total).

Aqui não há atalho por complemento: o evento de interesse é direto.

- Probabilidade de **um** servidor estar disponível: `p`
- Probabilidade de **todos os n** estarem disponíveis (independentes):

```
A(k=n) = pⁿ
```

**Verificação da fórmula** (teste de sanidade):
- Se p = 1: `A = 1ⁿ = 1` → serviço sempre disponível ✓
- Se p = 0: `A = 0ⁿ = 0` → serviço nunca disponível ✓
- Exemplo numérico: p = 0,9 e n = 3 → `A = 0,9³ = 0,729` (72,9%)
- Aumentar **n** diminui **A**: exigir mais réplicas de pé torna a operação
  mais frágil. Contraste com o caso de leitura, que é justamente o que
  diferencia consulta de atualização.

## 1.1.5. Caso geral: k qualquer (0 < k ≤ n)

Os dois casos anteriores são extremos. Para generalizar, o serviço fica
disponível quando **X ≥ k**, ou seja, quando o número de servidores disponíveis
for **k, ou k + 1, ou k + 2, ..., ou n**. Esses cenários são mutuamente
exclusivos, então basta **somar as probabilidades** de cada um:

```
A = P(X = k) + P(X = k+1) + ... + P(X = n)
```

Agora preciso calcular **P(X = i)** para cada i de k até n: a probabilidade de
exatamente **i** servidores estarem disponíveis.

Suponha que escolhemos quais i servidores (de um total de n) estão de pé. Há
`C(n, i)` maneiras de escolher esses i servidores. Cada um dos i disponíveis
contribui com `p`, e cada um dos `n − i` indisponíveis contribui com `1 − p`:

```
P(X = i) = C(n, i) · pⁱ · (1 − p)ⁿ⁻ⁱ
```

Substituindo na soma, obtenho **a fórmula geral de disponibilidade**:

```
                n
A(k)  =   Σ    C(n,i) · pⁱ · (1 − p)ⁿ⁻ⁱ
              i=k
```

em que `C(n,i)` é o binomial (combinação) `n! / (i! · (n−i)!)`.

### 1.1.5.1. Confirmação de que a fórmula geral envolve os casos extremos

Uma propriedade interessante é que a fórmula geral **contém** os dois casos
derivados antes, o que valida a dedução:

- **k = 1:** a soma vai de i = 1 até n. O termo que fica de fora é só o
  `i = 0` ("nenhum servidor de pé"), logo:

  ```
  A = Σ (i=1..n) = 1 − P(X=0) = 1 − (1 − p)ⁿ   ✓  (bate com o caso k=1)
  ```

- **k = n:** a soma tem um único termo, i = n:

  ```
  A = C(n,n) · pⁿ · (1−p)⁰ = 1 · pⁿ · 1 = pⁿ   ✓  (bate com o caso k=n)
  ```

Isso confirma que a fórmula geral é consistente com as deduções dos casos
extremos e cobre qualquer k intermediário.

---

# Exercício 1.2 — Implementação e validação da fórmula

Nesta parte implemento a fórmula derivada no Exercício 1.1 em Python, mostro
como a disponibilidade varia com n, k e p, e valido tudo por meio de um
simulador estocástico. A linguagem escolhida foi **Python** (com as
bibliotecas `numpy`, `pandas` e `matplotlib`).

## 1.2.1. Cálculo analítico

Implementei a fórmula geral como a função `disponibilidade(n, k, p)`. Ela faz
exatamente a soma de i = k até i = n:

```python
import math

def combinacao(n, i):
    """Número de combinações C(n, i) = n! / (i! (n-i)!)."""
    return math.comb(n, i)

def disponibilidade(n, k, p):
    soma = 0.0
    for i in range(k, n + 1):
        soma += combinacao(n, i) * (p ** i) * ((1 - p) ** (n - i))
    return soma
```

*(Nota: a estrutura desta função — usar `math.comb` e o laço de soma — foi
formada com auxílio de IA. Entendi cada linha: `math.comb(n, i)` calcula a
combinação C(n,i), `p ** i` é p elevado a i, `(1-p) ** (n-i)` é o complemento
elevado, e o `for` acumula os termos na variável `soma`.)*

**Validação inicial:** rodando a função com n = 3 e p = 0,9, confirmei que a
fórmula geral reproduz corretamente os casos extremos e o caso intermediário:

| Caso | Fórmula geral | Esperado | Bate? |
|------|---------------|----------|-------|
| k = 1 | 0.9990 | `1−(1−p)³ = 0.9990` | ✓ |
| k = n | 0.7290 | `p³ = 0.7290` | ✓ |
| k = 2 | 0.9720 | `C(3,2)·p²·(1−p) + C(3,3)·p³ = 0.9720` | ✓ |

### Tabela analítica

Para visualizar o comportamento, gerei uma tabela variando n ∈ {1, 2, 3, 5, 10},
p ∈ {0.7, 0.85, 0.95, 0.99} e k nos três critérios pedidos (k = 1, k = n/2 e
k = n). O trecho da tabela (disponibilidade analítica) está salvo no arquivo
`Exercicio-1.2/tabela_analitica.csv`. Uma amostra:

| n | k | critério | p | disponibilidade |
|---|-------|----------|-------|-----------------|
| 3 | 1 | k=n/2 | 0.70 | 0.973000 |
| 3 | 3 | k=n | 0.70 | 0.343000 |
| 5 | 2 | k=n/2 | 0.70 | 0.969220 |
| 10 | 5 | k=n/2 | 0.70 | 0.952651 |
| 10 | 10 | k=n | 0.70 | 0.028248 |
| 10 | 10 | k=n | 0.99 | 0.904382 |

Leituras importantes que tirei da tabela:
- **k = n (escrita)** é muito sensível ao número de réplicas: com n = 10 e
  p = 0.7, a disponibilidade cai para apenas **2.8%**. Exigir todos de pé é
  difícil.
- **k = 1 (leitura)** é altamente tolerante: já com n = 5 e p = 0.7, a
  disponibilidade é **99.75%**.
- **k = n/2** fica entre os dois extremos, como esperado.

### Gráficos 2D do cálculo analítico

Gerei três gráficos 2D (disponibilidade × p), um para cada critério, com uma
curva por valor de n. Arquivos gerados em `Exercicio-1.2/`:

- `grafico_analitico_k=1.png`
- `grafico_analitico_k=n_2.png`
- `grafico_analitico_k=n.png`

Observação visual: no gráfico de **k = 1** as curvas ficam "esmagadas" no topo
(disponibilidade próxima de 1 já com p médio); no de **k = n** elas sobem bem
mais devagar; e no de **k = n/2** ficam num meio-termo. Essa diferença visual
evidencia o papel de k na tolerância do serviço.

## 1.2.2. Simulador estocástico

Para validar a fórmula na prática, implementei um simulador que em cada
**rodada** sorteia o estado de cada servidor:

1. Para cada servidor, gera um número aleatório `u` em [0, 1]:
   - se `u ≤ p` → servidor disponível
   - senão → servidor indisponível
2. Conta quantos servidores estão disponíveis.
3. Verifica se o serviço permaneceu operacional: nº disponíveis ≥ k.

Repetindo isso por **100.000 rodadas** em cada configuração (n, k, p), calculei
a **frequência experimental** de disponibilidade (proporção de rodadas
bem-sucedidas) e comparei com o valor analítico.

*(Nota: o desenho do simulador — a mecânica de sortear por servidor usando
`rng.random() <= p` e acumular o número de sucessos — foi formado com auxílio
de IA. Compreendi o funcionamento: o `random.random()` produz um valor uniforme
em [0,1], compará-lo com `p` é a forma de simular Bernoulli, e a semente
fixa `random.Random(42)` garante que os resultados sejam reproduzíveis.)*

Principais funções do simulador:

```python
def simular_rodada(n, p, rng):
    disponiveis = 0
    for _ in range(n):
        u = rng.random()
        if u <= p:
            disponiveis += 1
    return disponiveis

def simular(n, k, p, rodadas=100000, rng=None):
    if rng is None:
        rng = random.Random()
    sucessos = 0
    for _ in range(rodadas):
        if simular_rodada(n, p, rng) >= k:
            sucessos += 1
    return sucessos / rodadas
```

### Resultados experimentais x analíticos (tabela)

A tabela completa está em `Exercicio-1.2/tabela_simulacao.csv`. Uma amostra dos
resultados (100.000 rodadas, semente fixa):

| n | k | critério | p | analítico | simulado | diferença |
|---|-------|----------|-------|-----------|----------|-----------|
| 2 | 2 | k=n | 0.85 | 0.722500 | 0.722430 | 0.000070 |
| 3 | 3 | k=n | 0.70 | 0.343000 | 0.343910 | 0.000910 |
| 5 | 5 | k=n | 0.70 | 0.168070 | 0.170040 | 0.001970 |
| 5 | 5 | k=n | 0.85 | 0.443705 | 0.441080 | 0.002625 |
| 10 | 10 | k=n | 0.70 | 0.028248 | 0.027900 | 0.000348 |
| 10 | 10 | k=n | 0.99 | 0.904382 | 0.902720 | 0.001662 |

A **diferença máxima** observada entre o valor analítico e o simulado foi de
aproximadamente **0.0026** (0,26 pontos percentuais). Isso é o erro amostral
esperado de uma simulação com 100.000 rodadas: quanto maior o número de
rodadas, menor a diferença.

### Gráficos 2D comparando teoria e prática

Gerei também gráficos 2D sobrepondo as curvas **analítica** (linha sólida) e
**simulada** (linha tracejada) para cada critério. Arquivos gerados em
`Exercicio-1.2/`:

- `grafico_simulacao_k=1.png`
- `grafico_simulacao_k=n_2.png`
- `grafico_simulacao_k=n.png`

Nos gráficos, as curvas analítica e simulada ficam praticamente **sobrepostas**,
o que evidencia que a simulação converge para a fórmula teórica — validando a
dedução do Exercício 1.1.

*(Nota: a montagem dos gráficos com `matplotlib` (laços por critério, `plot`
sobrepondo séries, eixo, grade, legenda e `savefig`) foi formada com auxílio de
IA; os rótulos e a interpretação foram feitas por mim.)*

## 1.2.3. Conclusão do Exercício 1.2

- A fórmula analítica foi implementada com sucesso e reproduz os casos
  extremos K = 1 e K = n.
- A tabela e os gráficos mostram que **k = 1** maximiza a disponibilidade
  (leitura tolerante a falhas) e **k = n** minimiza (escrita exige quórum
  total). Quanto maior n, mais nítida essa diferença.
- O simulador estocástico validou a fórmula: as frequências experimentais
  ficaram todas muito próximas dos valores teóricos (diferença máxima ~0.26%),
  confirmando que a dedução matemática está correta.

---

# Conclusão geral

A disponibilidade de um serviço replicado em n servidores, com probabilidade
individual p de cada servidor estar disponível e exigência de k servidores
disponíveis, é dada por:

```
                n
A(k)  =   Σ    C(n,i) · pⁱ · (1 − p)ⁿ⁻ⁱ
              i=k
```

- Para **k = 1** (consulta): `A = 1 − (1 − p)ⁿ`
- Para **k = n** (atualização): `A = pⁿ`

A combinação de dedução teórica, implementação analítica e simulação
estocástica mostrou resultados consistentes: a teoria e a prática convergem, e
a replicação **aumenta** a disponibilidade para leituras e **reduz** para
escritas. Esse é o trade-off essencial em sistemas distribuídos: mais réplicas
melhoram a tolerância a falhas em consultas, mas dificultam a consistência em
atualizações.

---

## Estrutura de arquivos deste trabalho

```
Computação Distribuida/
├── README.md                      <- este documento
├── Exercicio-1.1/
│   ├── deducao.md                 <- dedução passo a passo
│   └── (README.md foi movido para a raiz)
├── Exercicio-1.2/
│   ├── analitico.py               <- implementação da fórmula + tabela + gráficos
│   ├── simulador.py               <- simulador estocástico + tabela + gráficos
│   ├── tabela_analitica.csv       <- tabela analítica
│   ├── tabela_simulacao.csv       <- tabela experimental x analítico
│   ├── grafico_analitico_*.png    <- gráficos 2D analíticos
│   └── grafico_simulacao_*.png    <- gráficos 2D comparativos
└── venv/                          <- ambiente virtual Python com as dependências
```

---

*Obrigado pela atenção. Qualquer dúvida estou à disposição.*

---

## Nota de transparência sobre uso de IA

Este trabalho contou com o auxílio de uma ferramenta de inteligência artificial
(assistente de codificação/programação). A IA foi utilizada:

1. **Na escrita:** organização, revisão e redação deste documento, e do texto
   das deduções.
2. **Na formação de algumas funções:** estrutura dos scripts `analitico.py` e
   `simulador.py` (funções de combinação/disponibilidade, mecânica de sorteio
   do simulador e montagem dos gráficos com `matplotlib`).

Deixei notas ao longo do texto indicando os trechos específicos em que a IA
auxiliou. Todos os passos foram revisados, compreendidos e validados por mim
antes da entrega, sendo de minha inteira responsabilidade o conteúdo final
deste trabalho.

*Amilton Rocha Holanda*