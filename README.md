# Assistente Financeiro Inteligente no WhatsApp

Projeto inicial de um assistente financeiro com IA para registrar gastos por mensagem de WhatsApp, consultar total do mês e controlar limite de orçamento.

## Funcionalidades já implementadas (MVP)
- Registro de gasto em linguagem simples (ex.: `mercado 130`).
- Categorização automática por palavras-chave (`alimentação`, `transporte`, `lazer`, `saúde`, `investimentos`, `outros`).
- Definição de limite mensal (ex.: `limite 2000`).
- Consulta de total gasto no mês e saldo disponível.
- Endpoint preparado para receber mídia (`image` e `audio`) com mensagem de placeholder para futura integração de OCR/STT.

## Arquitetura proposta para produção
1. **Canal WhatsApp Business API (Meta)**
   - Webhook recebe mensagens de texto, imagem e áudio.
2. **Camada de processamento IA**
   - NLP para extrair intenção, valor e categoria.
   - OCR (imagens de comprovantes) e STT (áudios).
3. **Camada de dados**
   - Armazenamento de gastos, metas, limites e histórico por usuário.
4. **Camada de inteligência financeira**
   - Alertas de estouro de orçamento.
   - Insights por categoria e previsão de saldo.
5. **Segurança e compliance (LGPD)**
   - Criptografia em trânsito e em repouso.
   - Minimização de dados pessoais.
   - Controle de retenção e exclusão de dados.
   - Sem acesso direto à conta bancária; atuação como assistente pessoal.

## Segurança (diretrizes)
- Verificar assinatura da Meta no webhook.
- Validar origem de mensagens e aplicar rate limit.
- Mascarar dados sensíveis em logs.
- Auditoria de ações críticas e trilha de consentimento LGPD.

## Como rodar
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Exemplo de uso local
```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"phone":"5511999999999","text":"mercado 130"}'
```

## Próximos passos recomendados
- Integrar com WhatsApp Cloud API (webhook real + envio de resposta).
- Implementar OCR (ex.: Tesseract ou API externa) e STT (ex.: Whisper).
- Adicionar autenticação por token e assinatura HMAC.
- Criar testes de integração do webhook com cenários de mídia.
- Subir banco gerenciado e observabilidade (métricas + tracing).
