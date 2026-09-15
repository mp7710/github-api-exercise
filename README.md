## 📚 Exercício GitHub API

Três tarefas práticas para explorar e analisar dados públicos do GitHub usando sua API.

### 🎯 Tarefas

#### **Tarefa 1: Explorar sua própria conta**
```bash
python tarefa1.py
```

**O que faz:**
- ✅ Faz requisição para `/users/{seu_username}`
- ✅ Lista todos os seus repositórios públicos
- ✅ Calcula o total de estrelas acumuladas
- 💾 Salva resultado em `tarefa1_resultado.json`

---

#### **Tarefa 2: Analisar projeto open-source**
```bash
python tarefa2.py
```

**O que faz:**
- ✅ Analisa um repositório famoso (ou à sua escolha)
- ✅ Extrai: estrelas, forks, issues abertas
- ✅ Identifica linguagens utilizadas
- ✅ Coleta informações adicionais (licença, tópicos, etc.)
- 💾 Salva resultado em `tarefa2_resultado_{owner}_{repo}.json`

**Exemplos de repositórios:**
- `numpy/numpy` - NumPy
- `pandas-dev/pandas` - Pandas
- `tensorflow/tensorflow` - TensorFlow
- `pytorch/pytorch` - PyTorch
- `scikit-learn/scikit-learn` - Scikit-learn

---

#### **Tarefa 3: Criar dataset personalizado**
```bash
python tarefa3.py
```

**O que faz:**
- ✅ Coleta dados de múltiplos repositórios
- ✅ Oferece dataset padrão ou entrada personalizada
- ✅ Gera estatísticas agregadas
- ✅ Calcula distribuição de linguagens
- 💾 Salva resultado em `tarefa3_resultado.json`

**Dataset padrão incluído:**
- numpy/numpy
- pandas-dev/pandas
- tensorflow/tensorflow
- pytorch/pytorch
- scikit-learn/scikit-learn

---

#### **Bônus: Visualizar as estatísticas**
```bash
python visualizar.py
```

**O que faz:**
- 📈 Lê o `tarefa3_resultado.json` gerado pela Tarefa 3
- 📊 Gera um gráfico de barras comparando estrelas e forks por repositório
- 🎨 Usa uma paleta segura para daltonismo, com rótulos diretos em cada barra
- 💾 Salva a imagem em `visualizacao.png`

Requer `matplotlib` (incluído no `requirements.txt`).

---

### 🚀 Como usar

1. **Clone o repositório:**
```bash
git clone https://github.com/mp7710/github-api-exercise.git
cd github-api-exercise
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute as tarefas:**
```bash
python tarefa1.py
python tarefa2.py
python tarefa3.py
```

---

### 📊 Exemplos de saída

Cada tarefa gera um arquivo JSON com os dados coletados:

**tarefa1_resultado.json** - Dados do usuário e repositórios
**tarefa2_resultado_{owner}_{repo}.json** - Análise de repositório específico
**tarefa3_resultado.json** - Dataset com múltiplos repositórios

---

### 🔑 Notas importantes

- A API do GitHub permite ~60 requisições por hora sem autenticação
- Para aumentar o limite para ~5000/hora, configure um **Personal Access Token**
- Defina a variável de ambiente antes de rodar: `export GITHUB_TOKEN=seu_token`
  (os scripts leem esse token automaticamente e o enviam no cabeçalho `Authorization`)
- Os scripts tratam o *rate limit* (403) e avisam quanto tempo esperar
- Os dados são coletados diretamente da API pública do GitHub

**Sobre issues x pull requests:** o endpoint `open_issues_count` (e a listagem
`/issues`) do GitHub **conta pull requests como issues**. Por isso a **Tarefa 2**
usa a *Search API* (`type:issue` e `type:pr`) para contar os dois separadamente.
Já a **Tarefa 3** mantém o `open_issues_count` por simplicidade — lembrando que
esse número inclui os PRs abertos.

---

### 📝 Estrutura dos dados

```json
{
  "coletado_em": "2026-09-15T...",
  "estatisticas": {
    "total_repositorios": 5,
    "total_estrelas": 447700,
    "media_estrelas": 89540.0
  },
  "repositorios": [
    {
      "nome_completo": "numpy/numpy",
      "estrelas": 32700,
      "forks": 12800,
      "issues_abertas": 2000,
      "linguagem": "Python"
    }
  ]
}
```

---


### 📄 Licença

MIT License
