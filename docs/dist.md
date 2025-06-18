# Artefatos Distribuídos

Após `npm run build`, os arquivos compilados são gerados em `dist/`:

- **app.module.js/.map/.d.ts**: Módulo raiz.
- Subpastas por módulo (`identify`, `logs`, etc.):
  - `.js`, `.js.map`, `.d.ts`
- `main.js`, `main.js.map`, `main.d.ts`: Ponto de entrada compilado.