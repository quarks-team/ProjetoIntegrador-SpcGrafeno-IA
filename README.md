# ENGLISH:

# CI/CD Pipeline Documentation

This documentation describes how the CI/CD pipeline works, how to interpret the logs generated at each stage, and how to fix errors and failures.

## 1. Pipeline Overview
The pipeline is configured to run automatically on different events:
- **Pushes** to branches other than `main`.
- **Pull requests** to the `main` branch.
- **Manual execution** via `workflow_dispatch`.

It includes the following stages:
1. Code checkout.
2. Python environment setup.
3. Dependency installation.
4. Unit and integration test execution.
5. Test coverage report generation.
6. Automated deployment (only for merges to the `main` branch).

## 2. How the Pipeline Works

### Events that trigger the pipeline:
- **Push:** When a commit is made to any branch other than `main`, the pipeline runs the build and test stages.
- **Pull request:** The pipeline is triggered when a pull request is opened or updated, ensuring that the `main` branch only receives validated code.
- **Manual Trigger:** The pipeline can be manually triggered via the GitHub interface (using `workflow_dispatch`).

### Pipeline Stages:
1. **Build:**
   - Code checkout.
   - Python environment setup.
   - Dependency installation.
   - Test execution and coverage report generation.
2. **Deploy:**
   - Only for merges to the `main` branch, the application is automatically deployed to the production environment.

## 3. Logs and Feedback

The CI/CD pipeline generates detailed logs for each step, allowing for easy identification of errors. These logs are available directly within the GitHub Actions interface and are displayed after the execution of each job.

### How to interpret the logs:
- **Build Steps:**
  - On success, the steps for dependency installation and test execution should complete without error messages.
  - If an error occurs during dependency installation (e.g., incompatible versions), the log will show which package failed to install.
  - The test coverage report will be displayed at the end of the test execution step, showing the percentage of code covered by unit and integration tests.

- **Deploy Steps (for merges to `main`):**
  - The deployment step log will show whether the login to Azure was successful and whether the application was deployed correctly.
  - If deployment fails, the logs will provide information about the failure (e.g., authentication error with Azure, artifact extraction failure, or environment configuration errors).

## 4. Fixing Common Errors or Failures

### Common Errors:
1. **Dependency Installation Failure:**
   - Check the `requirements.txt` file to ensure all dependencies are listed correctly with appropriate versions.
   - Upgrade the package manager (`pip install --upgrade pip`) before installing dependencies to avoid errors with outdated versions.

2. **Unit or Integration Test Failures:**
   - The `pytest` logs will show details about which tests failed and why.
   - Revisit the tested code and apply necessary fixes.

3. **Deployment Failure:**
   - Ensure the Azure authentication credentials (stored as `secrets`) are correct and valid.
   - Check the permissions configured in the deploy job to ensure the pipeline has the necessary access to the production environment.
   - If the problem is related to the artifact file, verify that the `release.zip` file was generated correctly during the build.

## 5. Accessing Test Reports and Coverage
- The test coverage report is generated after the test execution and can be accessed directly in the pipeline logs.

## 6. Pipeline Documentation
The complete configuration of the CI/CD pipeline is described in the YAML file located in the repository at `.github/workflows/`.

## 7. Configuration and Maintenance
- **Environments:** The pipeline is configured to run in the `Ubuntu-latest` environment.
- **Credentials:** Credentials for authentication with Azure and other sensitive variables are stored in the repository `secrets`.
- **Future Adjustments:** The pipeline can be adjusted directly in the YAML file to support new tests, environments, or tools.


# pt/BR:

# CI/CD Pipeline Documentation

Esta documentação descreve como a pipeline CI/CD funciona, como interpretar os logs gerados em cada etapa, e como corrigir erros e falhas.

## 1. Pipeline Overview
A pipeline está configurada para rodar automaticamente em diferentes eventos:
- **Pushes** para branches que não sejam a `main`.
- **Pull requests** para a branch `main`.
- **Execução manual** através do `workflow_dispatch`.

Ela inclui as seguintes etapas:
1. Verificação do código-fonte.
2. Configuração do ambiente Python.
3. Instalação de dependências.
4. Execução de testes unitários e de integração.
5. Geração de relatórios de cobertura de testes.
6. Deploy automatizado (apenas em merges para a branch `main`).

## 2. Funcionamento da Pipeline

### Eventos que disparam a pipeline:
- **Push:** Quando um commit é feito em qualquer branch, exceto `main`, a pipeline é executada, rodando as etapas de build e teste.
- **Pull request:** A pipeline é acionada quando um pull request é aberto ou atualizado, garantindo que a branch `main` receba código validado.
- **Manual Trigger:** A pipeline pode ser acionada manualmente via interface (usando `workflow_dispatch`).

### Estágios da Pipeline:
1. **Build:**
   - Verificação do código (checkout).
   - Configuração do ambiente Python.
   - Instalação de dependências.
   - Execução de testes e geração de relatório de cobertura.
2. **Deploy:**
   - Somente em merges para a branch `main`, a aplicação é implantada automaticamente no ambiente de produção.

## 3. Logs e Feedback

A pipeline CI/CD gera logs detalhados para cada etapa, permitindo fácil identificação de erros. Estes logs estão disponíveis diretamente na interface do GitHub Actions e são exibidos logo após a execução de cada job.

### Como interpretar os logs:
- **Build Steps:**
  - Em caso de sucesso, as etapas de instalação de dependências e execução de testes devem passar sem mensagens de erro.
  - Caso algum erro ocorra durante a instalação de dependências (por exemplo, versões incompatíveis), o log exibirá qual pacote falhou na instalação.
  - O relatório de cobertura de testes será exibido no final da etapa de testes, mostrando a porcentagem de código coberta pelos testes unitários e de integração.

- **Deploy Steps (para merges em `main`):**
  - O log da etapa de deploy mostrará se o login no Azure foi bem-sucedido e se a aplicação foi implantada corretamente.
  - Se o deploy falhar, os logs exibirão informações sobre a falha (por exemplo, erro de autenticação com o Azure, falha na extração do artefato ou erros de configuração do ambiente).

## 4. Corrigindo Possíveis Erros ou Falhas

### Erros Comuns:
1. **Falha na Instalação de Dependências:**
   - Verifique o arquivo `requirements.txt` para garantir que todas as dependências estão listadas corretamente com as versões apropriadas.
   - Atualize o gerenciador de pacotes (`pip install --upgrade pip`) antes de instalar as dependências para evitar erros com versões antigas.

2. **Falha nos Testes Unitários ou de Integração:**
   - Os logs do `pytest` mostrarão detalhes sobre quais testes falharam e o motivo da falha.
   - Revisite o código testado e faça as correções necessárias.

3. **Falha no Deploy:**
   - Certifique-se de que as credenciais de autenticação do Azure (armazenadas como `secrets`) estão corretas e válidas.
   - Verifique as permissões configuradas no job de deploy para garantir que o pipeline tem acesso necessário ao ambiente de produção.
   - Se o problema for relacionado ao arquivo de artefato, confirme que o arquivo `release.zip` foi gerado corretamente durante o build.

## 5. Acesso aos Relatórios e Cobertura de Testes
- O relatório de cobertura de testes é gerado após a execução dos testes e pode ser acessado diretamente nos logs do pipeline.

## 6. Documentação da Pipeline
A configuração completa da pipeline CI/CD está descrita no arquivo YAML localizado no repositório em `.github/workflows/`.

## 7. Configuração e Manutenção
- **Ambientes:** O pipeline está configurado para rodar em ambiente `Ubuntu-latest`.
- **Credenciais:** As credenciais para autenticação no Azure e outras variáveis sensíveis estão armazenadas nos `secrets` do repositório.
- **Ajustes futuros:** A pipeline pode ser ajustada diretamente no arquivo YAML para suportar novos testes, ambientes ou ferramentas.

# ENGLISH:

# Data Insertion and Error Handling Documentation
This document explains the data insertion process into the ia_duplicate_prediction table, covering the ETL steps, insertion, error handling, and the logging generated to track and monitor the process.

## 1. ETL Process Structure
The ETL process consists of the following steps:

- ***Extraction***: Data is loaded from an input `.xlsx` file.
- ***Transformation***: Data undergoes various transformations to ensure it is in the required format. Transformations include:
   - Segment detection (e.g., "Endorser," "Fund," "Commerce") based on content within the input columns.
   - Calculation of installments (`installment`), month due (`month_due_date`), and quarter due (`quarter_due_date`).
   - One-Hot Encoding for categorical columns (`payment_place`, `segment`, and `kind`).
   - Definition of a `result` column to indicate the record’s status (`1` for finished, `0` for canceled).
- ***Loading***: Transformed data is inserted into the PostgreSQL database’s `ia_duplicate_prediction` table.

## 2. Data Insertion into the `ia_duplicate_prediction` Table
The transformed data is inserted into the `ia_duplicate_prediction` table using a prepared SQL query that dynamically includes columns generated by the One-Hot Encoding process. To ensure data integrity and efficient insertion:

- Each record is inserted individually, with logs detailing successes and failures.
- Dynamic columns (generated by One-Hot Encoding) are automatically identified and included in the insertion query.
- Database connection is managed by a custom PostgreSQL connection class, `PostgresConnection`.

## 3. Error Handling and Fault Recovery
During the insertion process, certain records may fail due to issues like data type mismatches, unexpected null values, or database integrity constraints. To handle these cases:

- Error Logging: If an error occurs during record insertion, the error is captured and recorded in a log file (`insercao_dados.log`) with:
   - The affected record ID.
   - A detailed error message to aid in diagnosis.
- Process Continuity: After logging an error, the process continues with subsequent records, avoiding interruptions and ensuring the highest possible success rate.

## 4. Logging and Monitoring
Execution logs are automatically generated in the file `insercao_dados.log` and include:

- Success messages for each correctly inserted record, with the record ID.
- Error messages with the record ID and a detailed error description when insertion fails.

These logs serve to:

- Facilitate the review of the ETL and insertion processes.
- Quickly identify problematic records that may require review or data correction.
- Document the process’s performance and integrity over time.
  
## 5. Acceptance Criteria
Data insertion is considered successful if the following criteria are met:

- ***Accuracy***: All eligible data is correctly inserted into the `ia_duplicate_prediction table`.
- ***Log Documentation***: Every record has detailed insertion logs. In case of failures, error messages are clear and indicate the affected record ID.
- ***Fault Recovery***: The process is resilient to failures, recording errors and progressing to the next records.

# pt/br:

# Documentação de Inserção de Dados e Tratamento de Erros
Este documento explica o processo de inserção de dados na tabela ia_duplicate_prediction, abordando as etapas de ETL, inserção, tratamento de erros, e os logs gerados para rastreamento e monitoramento do processo.

## 1. Estrutura do Processo ETL
O processo de ETL consiste nas seguintes etapas:

- ***Extraction***: Os dados são carregados a partir de um arquivo de entrada em formato `.xlsx`.
- ***Transformação***: Os dados passam por várias transformações para garantir que estejam no formato necessário. As transformações incluem:
   - Detecção de segmentos (e.g., "Endossante", "Fundo", "Comércio") com base no conteúdo das colunas de entrada.
   - Cálculo de parcelas (`installment`), mês de vencimento (`month_due_date`) e trimestre de vencimento (`quarter_due_date`).
   - Codificação One-Hot para colunas categóricas (`payment_place`, `segmento`, e `kind`).
   - Definição de uma coluna `result` para indicar o status do registro (`1` para finalizado, `0` para cancelado).
- ***Loading***: Os dados transformados são inseridos na tabela `ia_duplicate_prediction` do banco de dados PostgreSQL.

## 2. Inserção dos Dados na `Tabela ia_duplicate_prediction`
Os dados transformados são inseridos na tabela `ia_duplicate_prediction` utilizando uma consulta SQL preparada para incluir dinamicamente colunas geradas pelo processo de One-Hot Encoding. Para garantir a integridade e eficiência do processo de inserção:

- Cada registro é inserido individualmente, com logs detalhando sucessos e falhas.
- As colunas dinâmicas (geradas pela codificação One-Hot) são identificadas e incluídas automaticamente na consulta de inserção.
- A conexão com o banco de dados é estabelecida através de uma classe de conexão PostgreSQL personalizada,`PostgresConnection`.

## 3. Tratamento de Erros e Recuperação de Falhas
Durante o processo de inserção, é possível que alguns registros falhem devido a problemas como violação de tipo de dados, valores nulos inesperados, ou restrições de integridade do banco de dados. Para lidar com essas situações:

- ***Registro de Erros***: Em caso de erro durante a inserção de um registro, o erro é capturado e registrado em um arquivo de log (`insercao_dados.log`) com:
   - ID do registro afetado.
   - Mensagem detalhada do erro para auxiliar no diagnóstico.
- ***Continuidade do Processo***: Após registrar um erro, o processo continua a inserção dos registros subsequentes, evitando interrupções e garantindo a maior taxa de sucesso possível.

## 4. Logs e Monitoramento
Os logs de execução são gerados automaticamente no arquivo `insercao_dados.log` e incluem:

- Mensagens de sucesso para cada registro inserido corretamente, com o ID do registro.
- Mensagens de erro com o ID do registro e uma descrição detalhada do erro ocorrido durante a tentativa de inserção.

Esses logs servem para:

- Facilitar a revisão do processo de ETL e inserção.
- Identificar rapidamente registros problemáticos que possam precisar de revisão ou correção de dados.
- Documentar o desempenho e a integridade do processo ao longo do tempo.
  
## 5. Critérios de Aceitação
A inserção de dados é considerada bem-sucedida se os seguintes critérios forem atendidos:

- ***Precisão***: Todos os dados elegíveis são inseridos corretamente na tabela `ia_duplicate_prediction`.
- ***Documentação de Logs***: Todos os registros têm logs de inserção detalhados. Em caso de falhas, as mensagens de erro são claras e indicam o ID do registro afetado.
- ***Recuperação de Falhas***: O processo é resiliente a falhas, registrando erros e avançando para os próximos registros.
