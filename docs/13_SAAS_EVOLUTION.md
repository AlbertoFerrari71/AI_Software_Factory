# 13 — SaaS Evolution

## 1. Strategia

Il progetto nasce local-first ma deve poter evolvere in SaaS.

La regola è:

```text
SaaS-ready nella progettazione.
Non SaaS-premature nell'implementazione.
```

---

## 2. Componenti SaaS futuri

- workspace;
- multiutente;
- ruoli;
- permessi;
- audit log persistente;
- billing;
- limiti consumo;
- OAuth;
- secrets vault;
- sandbox code execution;
- connettori GitHub/GitLab;
- connettori MCP;
- marketplace template;
- analytics qualità;
- scoring affidabilità agenti.

---

## 3. Componenti da NON implementare nel primo MVP

- billing;
- multi-tenancy reale;
- OAuth;
- deploy cloud;
- marketplace;
- esecuzione codice remota;
- secret vault completo.

---

## 4. Scelte da preservare ora

Per restare SaaS-ready:

- usare modelli dati chiari;
- separare core e adapter;
- tracciare decisioni;
- prevedere audit log;
- non accoppiare tutto al filesystem locale;
- non accoppiare tutto a un unico vendor.
