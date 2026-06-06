# Scheduling API — MVP

API de agendamentos para espaços de estética (barbearias, salões, spas).

## Stack

- **FastAPI** + **SQLAlchemy async** + **PostgreSQL**
- Python 3.12

## Subindo o projeto

```bash
cp .env.example .env
docker-compose up --build
```

Acesse a documentação interativa em: http://localhost:8000/docs

---

## Fluxo básico de uso

### 1. Criar estabelecimento

```bash
curl -X POST http://localhost:8000/establishments/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Barbearia do João", "type": "barbershop", "phone": "83999999999"}'
```

### 2. Criar funcionário

```bash
curl -X POST http://localhost:8000/employees/ \
  -H "Content-Type: application/json" \
  -d '{
    "establishment_id": "<establishment_id>",
    "name": "Carlos Silva",
    "role": "Barbeiro"
  }'
```

### 3. Criar serviço

```bash
curl -X POST http://localhost:8000/services/ \
  -H "Content-Type: application/json" \
  -d '{
    "establishment_id": "<establishment_id>",
    "name": "Corte + Barba",
    "duration_minutes": 45,
    "price": 55.00
  }'
```

### 4. Cadastrar regra de disponibilidade (o "despertador")

Segunda a sexta, 08h–18h, slots de 30 minutos:

```bash
curl -X POST http://localhost:8000/schedule-rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "<employee_id>",
    "days_of_week": [0, 1, 2, 3, 4],
    "start_time": "08:00:00",
    "end_time": "18:00:00",
    "slot_duration_minutes": 30,
    "valid_from": "2025-01-01"
  }'
```

### 5. Consultar disponibilidade

Os slots são gerados automaticamente na primeira consulta:

```bash
curl "http://localhost:8000/availability/?employee_id=<employee_id>&from_date=2025-06-09&to_date=2025-06-13"
```

### 6. Cadastrar cliente

```bash
curl -X POST http://localhost:8000/clients/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Pedro Gabriel", "phone": "83988888888"}'
```

### 7. Agendar

```bash
curl -X POST http://localhost:8000/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "slot_id": "<slot_id>",
    "client_id": "<client_id>",
    "service_id": "<service_id>"
  }'
```

### 8. Cancelar agendamento

```bash
curl -X PATCH http://localhost:8000/appointments/<appointment_id>/cancel
```

---

## Estrutura

```
app/
├── main.py              # Entry point, lifespan, routers
├── config.py            # Settings (DATABASE_URL)
├── database.py          # Engine, session, Base
├── models/              # SQLAlchemy ORM
│   ├── establishment.py
│   ├── employee.py      # + tabela employee_services (N:N)
│   ├── service.py
│   ├── schedule_rule.py # Regra recorrente (o "despertador")
│   ├── available_slot.py
│   ├── client.py
│   └── appointment.py
├── schemas/             # Pydantic (request/response)
├── routers/             # Endpoints por domínio
└── services/
    └── slot_generator.py  # Gera slots a partir das regras
```

## Próximos passos sugeridos

- [ ] Autenticação (JWT) separando owner / employee / client
- [ ] Alembic migrations para produção
- [ ] Endpoint para bloquear slots manualmente (folgas, feriados)
- [ ] APScheduler para pré-gerar slots diariamente em background
- [ ] Notificações por WhatsApp/SMS ao confirmar/cancelar
- [ ] Endpoint de relatório: agendamentos por período / funcionário
