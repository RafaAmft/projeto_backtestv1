# Gerenciamento de Arquivos Grandes

Este diretório contém scripts e configurações para gerenciar arquivos grandes de dados que não devem ser versionados diretamente no Git.

## Problema

Arquivos CSV, Excel e outros formatos de dados podem ser muito grandes (ex: `fundos_historico_nome_atual.csv` com 170MB), causando:
- Repositório lento para clonar
- Limites do GitHub (100MB por arquivo)
- Histórico de commits pesado

## Solução

### 1. Git LFS (Large File Storage)

Configuramos o Git LFS para rastrear automaticamente:
- `*.csv` - Arquivos CSV
- `*.xlsx`, `*.xls` - Planilhas Excel
- `*.json` - Arquivos JSON grandes
- `*.zip`, `*.tar.gz` - Arquivos compactados

### 2. Storage Externo

Para arquivos muito grandes ou dados que mudam frequentemente:
- Google Drive
- Amazon S3
- Outros serviços de cloud storage

## Como Usar

### Git LFS (Automático)

Arquivos com extensões configuradas são automaticamente gerenciados pelo Git LFS:

```bash
# Adicionar arquivo grande
git add fundos_historico_nome_atual.csv
git commit -m "Adiciona dados históricos de fundos"

# Verificar arquivos LFS
git lfs ls-files
```

### Download de Dados Externos

Use o script `download_large_files.py`:

```bash
# Listar fontes disponíveis
python scripts/data_download/download_large_files.py --list

# Download de arquivo específico
python scripts/data_download/download_large_files.py --source fundos_historico

# Download de todos os arquivos
python scripts/data_download/download_large_files.py --all

# Forçar re-download
python scripts/data_download/download_large_files.py --source fundos_historico --force
```

## Configuração

### Adicionar Nova Fonte de Dados

Edite o arquivo `download_large_files.py` e adicione na seção `data_sources`:

```python
"nova_fonte": {
    "url": "https://exemplo.com/arquivo.csv",
    "filename": "arquivo.csv",
    "description": "Descrição do arquivo",
    "size_mb": 100
}
```

### Configurar URLs Reais

Substitua as URLs de exemplo pelas URLs reais dos seus dados:
- Google Drive (compartilhamento público)
- Amazon S3
- APIs de dados financeiros
- Outros serviços

## Estrutura de Diretórios

```
data/
├── external/          # Arquivos grandes baixados
│   ├── fundos_historico_nome_atual.csv
│   └── acoes_historico.csv
├── cache/             # Cache do sistema (já configurado)
└── historical/        # Dados históricos pequenos (versionados)
```

## Boas Práticas

1. **Arquivos < 50MB**: Use Git LFS
2. **Arquivos > 50MB**: Use storage externo + script de download
3. **Dados que mudam frequentemente**: Sempre use storage externo
4. **Documente**: Sempre documente a origem e formato dos dados
5. **Validação**: Implemente validação de integridade dos downloads

## Troubleshooting

### Git LFS não funciona
```bash
# Reinstalar hooks
git lfs install

# Verificar configuração
git lfs track
```

### Download falha
- Verifique a URL
- Confirme se o arquivo existe
- Verifique permissões de rede
- Use `--force` para re-download

### Arquivo muito grande para GitHub
- Use storage externo
- Divida o arquivo em partes menores
- Comprima o arquivo (se apropriado) 