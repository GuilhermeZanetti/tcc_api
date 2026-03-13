# Guide to Production in Cloud — Judge API

Guia completo para deploy da Judge API em produção, cobrindo dimensionamento de recursos, opções de infraestrutura, configuração de Nginx, SSL, monitoramento e estratégias de escala.

---

## 1. Análise de Recursos por Componente

Antes de dimensionar qualquer VPS, é essencial entender o custo real de cada componente do sistema.

### 1.1 API (FastAPI + Hypercorn)

- **Modelo de concorrência:** async/ASGI — 100 requisições HTTP simultâneas são apenas 100 coroutines aguardando I/O. Não há thread por requisição.
- **RAM em idle:** ~250 MB (Python + FastAPI + Motor + dependências)
- **CPU:** praticamente desprezível para operações I/O-bound (inserir submission no MongoDB e enfileirar no Redis)
- **Bottleneck real:** pool de conexões MongoDB (`MONGODB_MAX_CONNECTIONS_COUNT=10` por padrão — aumentar para produção)

### 1.2 Worker RQ (o componente mais pesado)

O worker é **single-threaded**: processa **um job por vez**. Cada job spawna subprocessos para compilar e executar código. Os custos variam radicalmente por linguagem:

| Linguagem | RAM por execução | CPU por execução | Observação |
|-----------|-----------------|-----------------|------------|
| Python    | ~80 MB          | 0.3 vCPU        | Interpretado, rápido de iniciar |
| C / C++   | ~150 MB         | 0.5 vCPU        | Compila com gcc/g++, binário leve |
| Go        | ~200 MB         | 0.5 vCPU        | go build demora ~2s extra |
| JavaScript| ~120 MB         | 0.3 vCPU        | Node.js, startup rápido |
| PHP       | ~100 MB         | 0.3 vCPU        | Interpretado |
| Java      | ~400 MB         | 0.8 vCPU        | JVM startup ~1-2s, pesado |
| C#        | ~600 MB         | 1.0 vCPU        | `dotnet build` + `dotnet new` a cada job — o mais pesado |

**TLE_TIMEOUT=30s** significa que um job pode segurar um worker por até 30 segundos.

### 1.3 MongoDB (Replica Set rs0)

- **RAM mínima:** 512 MB (working set em cache)
- **RAM recomendada:** 2 GB (para evitar page faults com histórico de submissions)
- **CPU:** baixo para queries simples por UUID
- **Storage:** ~1 KB por submission; 100.000 submissions ≈ 100 MB

### 1.4 Redis

- **RAM:** ~50 MB em operação normal
- **CPU:** desprezível
- **Dados em memória:** jobs na fila + metadados RQ

---

## 2. Dimensionamento para 100 Requisições Simultâneas

### Distinção crítica

"100 requisições simultâneas" tem dois significados diferentes neste sistema:

**Cenário A — 100 HTTP POST /submissions ao mesmo tempo (fila)**
- A API aceita todas as 100 em ~100ms, cria os documentos no MongoDB e enfileira no Redis.
- Os workers processam a fila gradualmente.
- Tempo para zerar a fila depende do número de workers e das linguagens enviadas.

**Cenário B — 100 execuções de código acontecendo ao mesmo tempo**
- Requer 100 workers rodando em paralelo.
- Inviável em uma única VPS pequena (seria necessário ~60 GB de RAM apenas para workers).
- Exige arquitetura distribuída.

> **Para uma maratona de programação**, o Cenário A é o realista: os participantes submetem e aguardam na fila. O que importa é o **throughput** (quantas submissions/segundo o sistema consegue processar), não necessariamente processar todas ao mesmo tempo.

### Cálculo de throughput por número de workers

Assumindo mix de linguagens (Python/C/C++/Java/Go) com tempo médio de execução de **5 segundos** por job:

| Workers | Jobs/minuto | Fila de 100 limpa em |
|---------|-------------|----------------------|
| 2       | 24          | ~4 minutos           |
| 4       | 48          | ~2 minutos           |
| 8       | 96          | ~1 minuto            |
| 16      | 192         | ~30 segundos         |

---

## 3. Configurações de VPS

### 3.1 Configuração Mínima (budget / TCC / demonstração)

**Objetivo:** aceitar 100 submissões, processar com 2 workers simultâneos.

```
vCPU:    2 cores
RAM:     4 GB
Storage: 40 GB SSD
OS:      Ubuntu 22.04 LTS
```

**Serviços no mesmo host:**
- API (Hypercorn, 1 instância)
- MongoDB (replica set single-node)
- Redis
- 2x Worker RQ
- Nginx (reverse proxy)

**Limitações:**
- C# pode falhar por falta de RAM (dotnet build consome ~600 MB por job)
- MongoDB sem redundância (risco de perda de dados)
- Sem tolerância a falhas

**Provedores com este perfil (preço/mês estimado em 2025):**
- Hetzner CX22: 2 vCPU AMD, 4 GB RAM — ~€4,35/mês ✅ melhor custo-benefício
- DigitalOcean Basic Droplet: 2 vCPU, 4 GB RAM — ~$24/mês
- AWS EC2 t3.medium: 2 vCPU, 4 GB RAM — ~$30/mês
- Oracle Cloud Free Tier: 4 vCPU ARM, 24 GB RAM — **gratuito** ✅ melhor opção gratuita

---

### 3.2 Configuração Recomendada (produção real / maratona)

**Objetivo:** aceitar 100 submissões, processar com 4-6 workers, suportar C# e Java sem problemas.

```
vCPU:    4-6 cores
RAM:     8 GB
Storage: 80 GB SSD NVMe
OS:      Ubuntu 22.04 LTS
```

**Serviços:**
- API (Hypercorn, 1 instância, 2-4 workers Hypercorn)
- MongoDB (replica set single-node com backup automático)
- Redis
- 4x Worker RQ
- Nginx + Certbot (SSL)

**Provedores:**
- Hetzner CX32: 4 vCPU, 8 GB RAM — ~€8,50/mês ✅ recomendado
- Hetzner CPX31: 4 vCPU AMD, 8 GB RAM — ~€10,49/mês
- DigitalOcean: 4 vCPU, 8 GB RAM — ~$48/mês
- AWS EC2 t3.large: 2 vCPU, 8 GB RAM — ~$60/mês
- Linode/Akamai: 4 vCPU, 8 GB RAM — ~$48/mês

---

### 3.3 Configuração Alta Performance (múltiplas maratonas simultâneas)

**Objetivo:** 100 execuções verdadeiramente simultâneas.

```
vCPU:    16+ cores
RAM:     32 GB
Storage: 200 GB NVMe
OS:      Ubuntu 22.04 LTS
```

**Serviços:**
- API (múltiplas instâncias atrás de Nginx com load balancing)
- MongoDB Atlas ou replica set dedicado
- Redis (ElastiCache ou standalone)
- 12-16x Worker RQ
- Nginx + SSL

**Provedores:**
- Hetzner AX41-NVMe (dedicated): 6 cores/12 threads, 64 GB RAM — ~€54/mês
- Hetzner CCX43: 16 vCPU AMD, 64 GB RAM — ~€89/mês
- AWS EC2 c6i.4xlarge: 16 vCPU, 32 GB RAM — ~$550/mês
- DigitalOcean CPU-Optimized 16 vCPU: ~$320/mês

---

## 4. Deploy em VPS — Passo a Passo

### 4.1 Preparação do Servidor

```bash
# Atualizar o sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y docker.io docker-compose-plugin git nginx certbot python3-certbot-nginx ufw

# Habilitar e iniciar Docker
sudo systemctl enable docker
sudo systemctl start docker

# Adicionar usuário atual ao grupo docker (evitar sudo)
sudo usermod -aG docker $USER
newgrp docker

# Configurar firewall
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4.2 Clonar e Configurar o Projeto

```bash
# Clonar o repositório
git clone <url-do-repositorio> /opt/judge-api
cd /opt/judge-api

# Criar arquivo de variáveis de ambiente
cp local.env.example local.env   # ou criar manualmente
nano local.env
```

**Conteúdo do `local.env` para produção:**

```env
# Banco de dados
MONGODB_URL=mongodb://mongodb:27017/judge?replicaSet=rs0
MONGODB_DATABASE=judge
MONGODB_MAX_CONNECTIONS_COUNT=20
MONGODB_MIN_CONNECTIONS_COUNT=5

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_QUEUE=submissions

# Segurança — TROQUE para um UUID gerado aleatoriamente
API_KEY_MASTER=<uuid-forte-gerado-com-python3-c-import-uuid-print-uuid.uuid4()>

# Judge
TLE_TIMEOUT=30
IGNORE_TRAILING_WHITESPACE=true
IGNORE_EMPTY_LINES=false
CASE_SENSITIVE=true

# CORS — domínio do frontend
BACKEND_CORS_ORIGINS=["https://seu-dominio.com"]
```

### 4.3 docker-compose.prod.yml

Crie um arquivo separado para produção com múltiplos workers:

```yaml
# docker-compose.prod.yml
services:
  judge:
    build:
      context: .
      dockerfile: Dockerfile.judge
    container_name: judge
    volumes:
      - ./entrypoint.sh:/app/entrypoint.sh
    entrypoint: /app/entrypoint.sh
    # Hypercorn com múltiplos workers para a API
    command: hypercorn src.main:app --bind 0.0.0.0:8000 --workers 4
    depends_on:
      mongodb:
        condition: service_healthy
      redis:
        condition: service_started
    env_file: ./local.env
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE

  # Worker 1 — use réplicas para escalar horizontalmente
  worker:
    build:
      context: .
      dockerfile: Dockerfile.judge
    volumes:
      - ./entrypoint.sh:/app/entrypoint.sh
    entrypoint: /app/entrypoint.sh
    command: python -m src.worker
    depends_on:
      mongodb:
        condition: service_healthy
      redis:
        condition: service_started
    env_file: ./local.env
    restart: unless-stopped
    deploy:
      replicas: 4       # Ajuste conforme RAM disponível
      resources:
        limits:
          cpus: '1'
          memory: 1.5G  # Aumentado para suportar C# e Java
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL

  mongodb:
    hostname: mongodb
    container_name: mongodb
    image: mongo:5
    expose:
      - 27017
    restart: always
    volumes:
      - mongodb_data:/data/db
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongo localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    entrypoint: ["/usr/bin/mongod", "--bind_ip_all", "--replSet", "rs0"]

  mongo-init-replica:
    image: mongo:5
    depends_on:
      mongodb:
        condition: service_healthy
    entrypoint: ["bash", "-c", "sleep 5 && mongo --host mongodb:27017 --eval 'rs.initiate({_id: \"rs0\", members: [{_id: 0, host: \"mongodb:27017\"}]})'"]
    restart: "no"

  redis:
    hostname: redis
    container_name: redis
    image: redis:7-alpine
    expose:
      - 6379
    restart: always
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

  rq-dashboard:
    image: eoranged/rq-dashboard:latest
    container_name: rq-dashboard
    depends_on:
      redis:
        condition: service_started
    environment:
      - RQ_DASHBOARD_REDIS_URL=redis://redis:6379/0
    # Não expor publicamente — acesso via SSH tunnel
    expose:
      - "9181"
    restart: always
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL

volumes:
  mongodb_data:
```

**Iniciar em produção:**

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 5. Configuração do Nginx

### 5.1 Reverse Proxy com Rate Limiting

```nginx
# /etc/nginx/sites-available/judge-api
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=20r/s;

upstream judge_api {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name seu-dominio.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com;

    ssl_certificate     /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_session_cache   shared:SSL:10m;

    # Segurança
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000" always;

    # Limite de tamanho de payload (código em base64)
    client_max_body_size 5M;

    # Rate limiting
    limit_req zone=api_limit burst=50 nodelay;

    location / {
        proxy_pass         http://judge_api;
        proxy_http_version 1.1;
        proxy_set_header   Connection "";
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 10s;
    }

    # Bloquear acesso direto ao RQ Dashboard externamente
    location /rq {
        deny all;
    }
}
```

```bash
# Ativar o site
sudo ln -s /etc/nginx/sites-available/judge-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Obter certificado SSL gratuito
sudo certbot --nginx -d seu-dominio.com
```

---

## 6. Opções de Provedor Cloud

### 6.1 Hetzner Cloud (recomendado para custo-benefício)

Melhor relação custo-benefício para projetos acadêmicos e startups. Datacenter em Falkenstein/Nuremberg/Helsinki (Europa) ou Ashburn (EUA).

| Plano   | vCPU | RAM   | Preço/mês | Indicado para |
|---------|------|-------|-----------|---------------|
| CX22    | 2    | 4 GB  | ~€4,35    | TCC / demo    |
| CX32    | 4    | 8 GB  | ~€8,50    | Maratona real |
| CX42    | 8    | 16 GB | ~€17      | Alta carga    |
| CCX13   | 2    | 8 GB  | ~€13      | Mín. prod. C# |
| CCX23   | 4    | 16 GB | ~€27      | Recomendado   |

**Recursos extras úteis:**
- Volumes persistentes: €0,052/GB/mês (para backup do MongoDB)
- Load Balancer: €6/mês (para múltiplas instâncias da API)
- Snapshots automáticos: ~20% do custo do servidor

```bash
# CLI da Hetzner (hcloud) para automação
hcloud server create --name judge-prod --type cx32 --image ubuntu-22.04 --ssh-key minha-chave
```

---

### 6.2 DigitalOcean

Boa UX, CDN e managed databases integrados. Mais caro que Hetzner mas com mais serviços gerenciados.

| Droplet          | vCPU | RAM   | Preço/mês |
|------------------|------|-------|-----------|
| Basic 4GB        | 2    | 4 GB  | $24       |
| Basic 8GB        | 4    | 8 GB  | $48       |
| CPU-Opt 8GB      | 4    | 8 GB  | $84       |
| Managed MongoDB  | —    | —     | a partir de $15 |

**Vantagem:** Managed MongoDB Atlas-like (DO Databases) elimina a necessidade de gerenciar replica set manualmente.

---

### 6.3 AWS EC2

Mais complexo, mas com mais opções de autoscaling e integração com outros serviços AWS.

| Instância    | vCPU | RAM   | Preço/mês (on-demand) |
|--------------|------|-------|-----------------------|
| t3.medium    | 2    | 4 GB  | ~$30                  |
| t3.large     | 2    | 8 GB  | ~$60                  |
| c6i.xlarge   | 4    | 8 GB  | ~$137                 |
| c6i.2xlarge  | 8    | 16 GB | ~$275                 |

**Serviços complementares úteis:**
- **ElastiCache (Redis):** ~$25/mês (cache.t3.small)
- **DocumentDB (MongoDB-compatible):** ~$60/mês (db.t3.medium)
- **ECR:** registro de imagens Docker gratuito até 500 MB
- **Savings Plans / Reserved Instances:** até 70% de desconto

**Para TCC/pesquisa:** AWS oferece créditos acadêmicos via AWS Educate (~$200).

---

### 6.4 Google Cloud Platform (GCP)

| Instância     | vCPU | RAM   | Preço/mês |
|---------------|------|-------|-----------|
| e2-medium     | 2    | 4 GB  | ~$24      |
| e2-standard-4 | 4    | 16 GB | ~$97      |
| n2-standard-4 | 4    | 16 GB | ~$130     |

**Para TCC:** GCP oferece $300 de crédito gratuito por 90 dias.

---

### 6.5 Oracle Cloud (Free Tier — Melhor opção gratuita)

O Oracle Cloud Free Tier é **permanentemente gratuito** e inclui:

```
Ampere A1 (ARM):
  - Até 4 vCPU (ARM Cortex-A55)
  - Até 24 GB RAM
  - 200 GB de storage

VMs AMD:
  - 2x VM.Standard.E2.1.Micro (1/8 vCPU, 1 GB RAM cada)
```

**Considerações:**
- As instâncias ARM rodam Docker sem problemas com imagens multi-arch
- O Dockerfile.judge precisa suportar linux/arm64 (verificar se as linguagens compiladas funcionam)
- Ideal para TCC com orçamento zero
- Latência pode ser maior dependendo da região disponível

---

## 7. Escalabilidade Horizontal

Quando uma única VPS não é suficiente, separe os componentes em hosts distintos.

### 7.1 Arquitetura Multi-Node

```
Internet
    │
  [Nginx Load Balancer]  ← VPS 1: 2 vCPU, 2 GB (Nginx)
    │         │
[API Node 1] [API Node 2]  ← VPS 2 e 3: 2 vCPU, 4 GB cada
    │         │
  [Redis] (compartilhado)  ← VPS 4: 2 vCPU, 4 GB (Redis)
    │
[Worker Node 1..N]  ← VPS 5+: 4 vCPU, 8 GB cada (Workers RQ)
    │
[MongoDB Replica Set]  ← VPS 6: 4 vCPU, 8 GB (Primário)
                          VPS 7: 4 vCPU, 8 GB (Secundário)
```

**Variáveis de ambiente por nó:**

```env
# API Nodes (apontam para serviços externos)
MONGODB_URL=mongodb://mongo-primary:27017,mongo-secondary:27017/judge?replicaSet=rs0
REDIS_HOST=redis-host
REDIS_PORT=6379

# Worker Nodes (mesmas variáveis, sem expor porta 8000)
MONGODB_URL=mongodb://mongo-primary:27017,mongo-secondary:27017/judge?replicaSet=rs0
REDIS_HOST=redis-host
```

### 7.2 Escalar Workers Dinamicamente

Usando Docker Swarm (mais simples que Kubernetes):

```bash
# Inicializar Swarm no manager node
docker swarm init

# Deploy do stack
docker stack deploy -c docker-compose.prod.yml judge

# Escalar workers conforme demanda
docker service scale judge_worker=8

# Ver status
docker service ls
docker service ps judge_worker
```

---

## 8. Monitoramento

### 8.1 RQ Dashboard

Já incluído no docker-compose. Acesse via SSH tunnel para não expô-lo publicamente:

```bash
# No seu computador local
ssh -L 9181:localhost:9181 usuario@seu-servidor

# Acesse no browser: http://localhost:9181
```

### 8.2 Logs em Produção

```bash
# Ver logs de todos os serviços
docker compose -f docker-compose.prod.yml logs -f

# Logs apenas dos workers
docker compose -f docker-compose.prod.yml logs -f worker

# Últimas 100 linhas da API
docker compose -f docker-compose.prod.yml logs --tail=100 judge
```

### 8.3 Monitoramento de Recursos

```bash
# Uso de recursos por container em tempo real
docker stats

# Instalar htop para visão do host
sudo apt install -y htop
htop
```

### 8.4 Alertas com Uptime Kuma (opcional, gratuito)

```bash
# Adicionar ao docker-compose.prod.yml
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    volumes:
      - uptime_kuma_data:/app/data
    ports:
      - "3001:3001"
    restart: always
```

Monitore `GET /healthchecks` como liveness probe. Configure alertas por e-mail ou Telegram.

---

## 9. Backup e Persistência

### 9.1 Backup automático do MongoDB

```bash
#!/bin/bash
# /opt/scripts/backup-mongo.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/mongodb"
mkdir -p $BACKUP_DIR

docker exec mongodb mongodump \
  --uri="mongodb://localhost:27017/judge" \
  --archive \
  --gzip > "$BACKUP_DIR/judge_$DATE.gz"

# Manter apenas os últimos 7 backups
ls -t $BACKUP_DIR/*.gz | tail -n +8 | xargs -r rm

echo "Backup criado: judge_$DATE.gz"
```

```bash
# Agendar via cron (todo dia às 2h da manhã)
chmod +x /opt/scripts/backup-mongo.sh
crontab -e
# Adicionar: 0 2 * * * /opt/scripts/backup-mongo.sh
```

### 9.2 Restaurar Backup

```bash
docker exec -i mongodb mongorestore \
  --uri="mongodb://localhost:27017/judge" \
  --archive \
  --gzip < /opt/backups/mongodb/judge_20251201_020000.gz
```

---

## 10. Checklist de Segurança para Produção

- [ ] `API_KEY_MASTER` trocado para UUID aleatório forte (nunca o padrão `57fba00c...`)
- [ ] Porta 27017 (MongoDB) bloqueada no firewall — acessível apenas internamente
- [ ] Porta 6379 (Redis) bloqueada no firewall — acessível apenas internamente
- [ ] Porta 9181 (RQ Dashboard) bloqueada — acesso só via SSH tunnel
- [ ] HTTPS habilitado com certificado Let's Encrypt (`certbot`)
- [ ] Rate limiting no Nginx configurado
- [ ] `no-new-privileges:true` nos containers (já no docker-compose)
- [ ] `cap_drop: ALL` nos containers (já no docker-compose)
- [ ] Backups automáticos do MongoDB agendados
- [ ] `BACKEND_CORS_ORIGINS` restrito ao domínio do frontend
- [ ] Usuário não-root no servidor (sem login como `root`)
- [ ] Chaves SSH configuradas (desativar autenticação por senha: `PasswordAuthentication no`)
- [ ] `ufw` ou `iptables` com regras restritivas

---

## 11. Resumo de Recomendações

| Cenário                          | VPS Mínima               | Provedor Sugerido         | Workers |
|----------------------------------|--------------------------|---------------------------|---------|
| TCC / Demo / Testes              | 2 vCPU, 4 GB             | Hetzner CX22 (~€4/mês)    | 2       |
| Maratona pequena (<50 times)     | 4 vCPU, 8 GB             | Hetzner CX32 (~€8/mês)    | 4       |
| Maratona média (50-200 times)    | 4 vCPU, 16 GB            | Hetzner CCX23 (~€27/mês)  | 6       |
| Orçamento zero                   | 4 vCPU ARM, 24 GB        | Oracle Cloud Free Tier    | 4-6     |
| Alta performance (>200 times)    | 8+ vCPU, 32 GB           | Hetzner CCX43 (~€89/mês)  | 12-16   |

> **Regra prática:** cada worker RQ consome ~1 GB de RAM no pico (C#/Java). Some a isso ~1 GB para API + MongoDB + Redis + OS. Planeje assim: `RAM_total = (num_workers × 1.2 GB) + 3 GB de overhead`.
>
> **Exemplo:** 4 workers = (4 × 1.2) + 3 = **7.8 GB → escolha 8 GB.**
