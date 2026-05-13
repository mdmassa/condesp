# CONDESP - Sistema de Conhecimento de Despesa

Sistema Django para consulta e gestão de Elementos e Subelementos de Despesa da Prefeitura Municipal de Marabá, baseado na Portaria STN nº XXX/XXXX.

## Como executar projeto

1.
```bash
docker-compose up --build
```

2.
Acesse: http://localhost:8000

3.
Criar conta de administrador (opcional para acesso a funcionalidades além da consulta).
```bash
docker-compose exec web python manage.py createsuperuser
```

## Funcionalidades

- **Dashboard com Live Search** — filtra por código, nome ou descrição em tempo real
- **Importar Planilha** — upload de CSV ou Excel (.xlsx/.xls) com colunas `codigo`, `nome`, `descricao`
- **Editar Descrição** — refine os exemplos de itens de cada elemento
- **Admin Django** — gerenciamento completo via painel admin

## Formato da planilha para importação

| codigo | nome | descricao |
|--------|------|-----------|
| 3.3.90.30.00 | Material de Consumo | Papel A4, canetas... |
| 4.4.90.52.00 | Equipamento e Material Permanente | Computadores, impressoras... |

## Tecnologias

- Django 4.2 + PostgreSQL 15
- Bootstrap 5.3 + jQuery 3.7
- Docker + Docker Compose
