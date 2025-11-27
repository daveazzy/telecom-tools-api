# 📡 TelecomTools Suite v1.0.0

**Sistema Completo de Análise de Telecomunicações e RF**

Aplicação web moderna para análise de cobertura celular, medições de sinal, cálculos de engenharia de RF e visualização de torres celulares no mapa interativo.

---

## 🎯 Funcionalidades Principais

### ✅ **Busca de Torres Próximas**
- 📍 Localização em tempo real do usuário
- 🗺️ Mapa interativo com marcadores de torres
- 📊 1.929 torres brasileiras do Rio Grande do Norte
- 📏 Cálculo automático de distância (raio até 50km)
- 📡 Informações: operadora, tecnologia (2G/3G/4G/5G), coordenadas

### ✅ **Medições de Sinal**
- 📍 Captura ponto de medição com geolocalização
- 📊 Registra: força do sinal (dBm), qualidade, frequência, operadora
- 📈 Histórico de medições com filtros por operadora/tecnologia
- 🔄 Sincronização com servidor em tempo real

### ✅ **Análise RF - Calculadora Avançada**
- **Link Budget**: Cálculo de orçamento de enlace (TX power, ganhos, atenuação)
- **Path Loss**: Perda de percurso com modelos:
  - Friis (espaço livre)
  - Log-distance (urbano, suburbano, rural)
  - Okumura-Hata
- **Fresnel Zone**: Zona de Fresnel para visibilidade de enlace
- **Conversões**: dBm ↔ Watts, dBi ↔ Linear, etc

### ✅ **Mapa de Cobertura - Heatmap**
- 🌡️ Visualização de cobertura por cor
- 📊 Grid de análise configurável
- 🎯 Análise por operadora
- 📈 Estatísticas de cobertura

### ✅ **Relatórios**
- 📄 Gera relatórios em PDF
- 📊 Exporta dados em CSV
- 🎨 Gráficos de tendência de sinal
- 📋 Comparação entre operadoras

### ✅ **Speed Tests**
- ⚡ Medição de velocidade: download, upload, ping, jitter
- 📊 Histórico com filtros por ISP
- 📈 Estatísticas agregadas
- 🗓️ Análise temporal

### ✅ **Autenticação & Segurança**
- 🔐 Registro de novo usuário
- 🔑 Login com JWT
- 👤 Gerenciamento de perfil
- 🔒 Tokens com expiração

---

## 🚀 Como Iniciar

### Pré-requisitos
- Python 3.10+
- Node.js 20+
- pnpm ou npm

### 1️⃣ Instalação Rápida

```bash
# Backend
cd telecom-api
pip install -r requirements.txt

# Frontend  
cd frontend
pnpm install
```

### 2️⃣ Iniciar Servidor

**Terminal 1 - Backend:**
```bash
python start_backend.py
# ou
python run.py
# Backend rodará em http://127.0.0.1:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
pnpm dev
# Frontend rodará em http://localhost:3000
```

### 3️⃣ Acessar Aplicação

- 🌐 **Frontend**: http://localhost:3000
- 📚 **API Docs**: http://127.0.0.1:8000/docs
- 🗄️ **Database**: SQLite em `telecom.db`

### 4️⃣ Credenciais de Teste

```
Usuário: dave
Senha: senha123

Usuário: test
Senha: test123
```

---

## 📁 Estrutura do Projeto

```
telecom-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # Rotas da API
│   │       │   ├── auth.py     # Login/Registro
│   │       │   ├── towers.py   # Busca de torres
│   │       │   ├── signals.py  # Medições de sinal
│   │       │   ├── calculations.py  # RF Calcs
│   │       │   ├── reports.py  # Relatórios
│   │       │   └── ...
│   ├── integrations/
│   │   └── opencellid.py       # Parser CSV de torres
│   ├── services/               # Lógica de negócio
│   ├── models/                 # SQLAlchemy models
│   └── main.py                 # FastAPI app
│
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js pages
│   │   │   ├── login/
│   │   │   ├── dashboard/
│   │   │   ├── dashboard/map/
│   │   │   └── ...
│   │   ├── components/         # React components
│   │   └── lib/                # Utilities
│   └── package.json
│
├── assets/
│   └── erbs - RN.csv          # 1.929 torres do RN
│
├── start_backend.py           # Script backend
├── run.py                      # Script backend alt
└── requirements.txt            # Dependencies
```

---

## 🔑 Endpoints da API

### Autenticação
- `POST /api/v1/auth/register` - Registrar novo usuário
- `POST /api/v1/auth/login` - Fazer login (JWT)

### Torres
- `GET /api/v1/towers/nearby?latitude=X&longitude=Y&radius_km=5` - Torres próximas
- `POST /api/v1/towers` - Criar torre (admin)
- `GET /api/v1/towers` - Listar torres

### Medições de Sinal
- `POST /api/v1/signals` - Registrar medição
- `GET /api/v1/signals` - Listar medições do usuário
- `POST /api/v1/signals/heatmap` - Gerar heatmap

### Cálculos RF
- `POST /api/v1/calculations/link-budget` - Link Budget
- `POST /api/v1/calculations/path-loss` - Path Loss
- `POST /api/v1/calculations/fresnel-zone` - Fresnel Zone
- `POST /api/v1/calculations/power-conversion` - Conversões

### Relatórios
- `POST /api/v1/reports` - Criar relatório
- `GET /api/v1/reports` - Listar relatórios
- `POST /api/v1/reports/generate` - Gerar PDF/CSV

### Speed Tests
- `POST /api/v1/speed-tests` - Registrar speed test
- `GET /api/v1/speed-tests` - Histórico
- `GET /api/v1/speed-tests/statistics/summary` - Estatísticas

---

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados leve e portável
- **Pydantic** - Validação de dados
- **JWT** - Autenticação segura
- **Python 3.10+**

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Material-UI** - Componentes de UI profissionais
- **Leaflet.js** - Mapas interativos
- **Recharts** - Gráficos e visualizações
- **Zustand** - State management
- **Axios** - HTTP client

### DevOps
- **Uvicorn** - ASGI server
- **Webpack** - Bundler (Next.js)
- **SQLite** - Banco de dados

---

## 📊 Dados

### Torres Celulares
- **Fonte**: ERBs - Set25 (Instituto ANATEL)
- **Cobertura**: Rio Grande do Norte, Brasil
- **Total**: 1.929 torres celulares
- **Atributos**: 
  - Coordenadas (Latitude/Longitude em graus/minutos/segundos)
  - Operadora (TIM, Claro, Vivo, Oi, etc)
  - Tecnologias (2G, 3G, 4G, 5G)
  - Endereço
  - Município

### Formato de Dados de Torre
```json
{
  "id": 1,
  "cellid": "1000020255",
  "latitude": -5.5025,
  "longitude": -36.8567,
  "operator": "TIM",
  "technology": "4G",
  "distance_km": 2.5,
  "city": "Natal"
}
```

---

## 🔬 Cálculos Implementados

### 1. Link Budget
```
Link Budget = TX Power + TX Gain - Path Loss + RX Gain - RX Sensitivity
```

### 2. Path Loss (Log-Distance)
```
PL(dB) = PL₀ + 10n·log₁₀(d) + X_σ
onde:
  PL₀ = Path loss a 1m
  n = expoente (2-4 dependendo do ambiente)
  d = distância em metros
  X_σ = variação gaussiana
```

### 3. Fresnel Zone
```
F₁ = 0.5√[(λ·d₁·d₂)/(d₁+d₂)]
onde:
  λ = comprimento de onda
  d₁, d₂ = distâncias dos pontos terminais
```

---

## 🎓 Para Apresentação na Feira

### O que Demonstrar

1. **Login & Autenticação**
   - Registrar novo usuário
   - Fazer login com JWT
   - Visualizar perfil

2. **Mapa de Torres**
   - Usar localização em tempo real
   - Buscar torres próximas
   - Clicar para ver detalhes (operadora, distância, tecnologia)

3. **Cálculos de RF**
   - Preencher parâmetros de Link Budget
   - Mostrar resultado
   - Explicar o que significa cada valor

4. **Medições**
   - Registrar medição de sinal manualmente
   - Mostrar histórico
   - Gerar heatmap

5. **Relatórios**
   - Gerar relatório em PDF
   - Exportar dados em CSV

### Pontos Fortes

✨ **Interface Intuitiva** - Fácil de usar, visual atrativo
✨ **Dados Reais** - 1.929 torres brasileiras
✨ **Funcionalidades Completas** - Não é um prototipo, é um app real
✨ **Stack Moderno** - FastAPI + Next.js + TypeScript
✨ **Responsivo** - Funciona em desktop, tablet, mobile
✨ **Cálculos Precisos** - Fórmulas de engenharia reais

---

## 📝 Licença

Projeto educacional - Desenvolvimento: David Azzy

---

## 🤝 Suporte

Para dúvidas durante a apresentação:

1. **Verificar logs**: Ver terminal onde backend/frontend rodam
2. **Reiniciar**: Fechar e reabrir ambas as abas
3. **Limpar cache**: Abrir DevTools (F12) > Network > "Disable cache"
4. **Reset DB**: Deletar `telecom.db` e reiniciar (recria com dados de teste)

---

## 📞 Contato

**Desenvolvedor**: David Azzy  
**Instituição**: [Sua Faculdade]  
**Data**: Novembro 2025

---

**Obrigado por conferir o TelecomTools Suite! 🚀**
