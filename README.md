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
