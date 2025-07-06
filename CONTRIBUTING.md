# 🤝 Guia de Contribuição

Obrigado por considerar contribuir com o Sistema de Análise Financeira! 

## 🎯 Como Contribuir

### 📋 Reportando Bugs

1. Use o template de [Bug Report](.github/ISSUE_TEMPLATE.md)
2. Inclua informações detalhadas sobre o problema
3. Adicione logs de erro se disponíveis
4. Descreva os passos para reproduzir o bug

### ✨ Sugerindo Novas Funcionalidades

1. Abra uma issue com o label `enhancement`
2. Descreva a funcionalidade desejada
3. Explique o benefício para os usuários
4. Se possível, inclua mockups ou exemplos

### 🔧 Desenvolvendo

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie** uma branch para sua feature:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```
4. **Desenvolva** sua funcionalidade
5. **Teste** suas mudanças:
   ```bash
   python scripts/run_tests.py
   ```
6. **Commit** suas mudanças:
   ```bash
   git commit -m "feat: adiciona nova funcionalidade"
   ```
7. **Push** para sua branch:
   ```bash
   git push origin feature/nova-funcionalidade
   ```
8. **Abra** um Pull Request

## 📝 Padrões de Código

### 🐍 Python

- Use **Python 3.8+**
- Siga o **PEP 8** para estilo de código
- Use **type hints** quando possível
- Adicione **docstrings** para funções e classes
- Mantenha **cobertura de testes** alta

### 📁 Estrutura de Arquivos

```
📁 ProjetoFinal/
├── 🧠 core/           # Núcleo do sistema
├── 🔌 apis/          # Integrações com APIs
├── 📊 dashboard/     # Interface web
├── 📚 examples/      # Exemplos de uso
├── 🧪 test_*.py      # Testes automatizados
└── 📄 docs/          # Documentação
```

### 🧪 Testes

- Escreva testes para novas funcionalidades
- Mantenha testes existentes funcionando
- Use nomes descritivos para testes
- Inclua testes de casos de erro

### 📚 Documentação

- Atualize o README.md se necessário
- Adicione docstrings em português
- Documente APIs e interfaces
- Mantenha exemplos atualizados

## 🏷️ Convenções de Commit

Use o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Tipos de Commit

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Formatação, ponto e vírgula, etc.
- `refactor`: Refatoração de código
- `test`: Adicionando ou corrigindo testes
- `chore`: Mudanças em build, config, etc.

### Exemplos

```bash
git commit -m "feat: adiciona análise de renda fixa"
git commit -m "fix: corrige erro na API Binance"
git commit -m "docs: atualiza README com novas funcionalidades"
git commit -m "test: adiciona testes para carteira ideal"
```

## 🔍 Processo de Review

1. **Auto-review**: Revise seu próprio código antes de submeter
2. **Testes**: Certifique-se de que todos os testes passam
3. **Documentação**: Atualize documentação se necessário
4. **Pull Request**: Use o template fornecido
5. **Feedback**: Responda aos comentários do review

## 🚀 Deploy

- Mudanças são automaticamente testadas
- Pull Requests são revisados antes do merge
- Releases são criados para versões estáveis
- Documentação é atualizada automaticamente

## 📞 Suporte

Se você tiver dúvidas sobre como contribuir:

1. Abra uma issue com label `question`
2. Consulte a documentação existente
3. Verifique issues similares
4. Entre em contato com os mantenedores

## 🙏 Agradecimentos

Obrigado por contribuir para tornar este projeto melhor! 

---

**Lembre-se**: Qualquer contribuição, por menor que seja, é muito bem-vinda! 🎉 