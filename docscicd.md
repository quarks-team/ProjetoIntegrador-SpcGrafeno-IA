## Estrutura do YAML

### Explicação:
- **name:** Define o nome do pipeline.
- **on:** Define os eventos que acionam o pipeline.
  - **push:** Aciona o pipeline em pushs para branches, exceto a main.
  - **branches-ignore:** Lista de branches que não acionarão o pipeline (a main).
  - **pull_request:** Aciona o pipeline apenas em pull requests que visam a main.
  - **workflow_dispatch:** Permite a execução manual do workflow.

<pre><code>
name: Python CI Pipeline with Azure Deployment

# The pipeline will trigger on pushes to any branch, except main, and on pull requests to main
on:
  push:
    branches-ignore:
      - main  # Ignore direct pushes to the main branch
  pull_request:
    branches:
      - main  # Trigger the pipeline only for pull requests targeting the main branch
  workflow_dispatch: # Manual trigger for workflows
</code></pre>

## Job de Build

### Explicação:
- **jobs:** Define um ou mais jobs a serem executados.
  - **build:** Nome do job de construção (build).
  - **runs-on:** Especifica o ambiente em que o job será executado (neste caso, Ubuntu).
  - **steps:** Lista de etapas a serem executadas no job.
    - **Check out the code:** Utiliza a ação checkout para obter o código do repositório.

<pre><code>
jobs:
  build:
    runs-on: ubuntu-latest  # Define que a pipeline rodará em um ambiente Ubuntu

    steps:
      # Primeiro, verifica o código do repositório
      - name: Check out the code
        uses: actions/checkout@v3
</code></pre>

### Continuação do Job de Build

- **Set up Python:** Configura a versão do Python (a mais recente disponível).

<pre><code>
      # Set up Python with the latest stable version
      - name: Set up Python 3.x
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'  # Use the latest stable version of Python
</code></pre>

- **Install dependencies:** Atualiza o pip e instala as dependências do projeto especificadas no `requirements.txt`.

<pre><code>
      # Install the dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip  # Upgrade pip
          pip install -r backendPython/requirements.txt  # Install project dependencies
</code></pre>

- **Run tests:** Navega para o diretório `backendPython` e executa os testes usando pytest, gerando um relatório em formato XML.

<pre><code>
      # Run unit tests and integration tests
      - name: Run tests
        run: |
          cd backendPython
          pytest --junitxml=results.xml  # Run tests with pytest and generate a report
</code></pre>

- **Generate coverage report:** Instala a biblioteca coverage, executa os testes para coletar dados de cobertura, e gera relatórios de cobertura tanto no console quanto em formato XML.

<pre><code>
      # Generate coverage report
      - name: Generate coverage report
        run: |
          pip install coverage  # Install the coverage library
          coverage run -m pytest  # Run tests for coverage
          coverage report -m  # Generate the coverage report
          coverage xml  # Export the report in XML for CI tools
</code></pre>

- **Test and Coverage Passed:** Se todos os testes forem bem-sucedidos, imprime uma mensagem indicando que está pronto para mesclar.

<pre><code>
      # If tests pass, the pipeline indicates success
      - name: Test and Coverage Passed
        if: success()
        run: echo "All tests passed, ready for merge!"
</code></pre>

- **Tests or Lint Failed:** Se qualquer etapa falhar, imprime uma mensagem e encerra o job com erro.

<pre><code>
      # If any step fails, the pipeline will be blocked
      - name: Tests or Lint Failed
        if: failure()
        run: |
          echo "There were failures in the tests or linting."
          exit 1
</code></pre>

## Job de Deploy

### Explicação:
- **deploy:** Nome do job de implantação (deploy).
- **runs-on:** Especifica que o job será executado em um ambiente Ubuntu.
- **needs:** Define que este job depende do job de build, ou seja, só será executado após a conclusão do job de build.
- **if:** Condição que verifica se o branch atual é a main. Isso garante que o deploy só ocorra quando houver uma mesclagem na main.

<pre><code>                       
  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'  # Trigger deploy only on main branch
</code></pre>

- **environment:** Define o ambiente de produção onde a aplicação será implantada.

<pre><code>  
    environment:
      name: 'Production'
      url: ${{ steps.deploy-to-webapp.outputs.webapp-url }}
</code></pre>

- **permissions:** Concede permissões necessárias, como a capacidade de solicitar um token JWT.

<pre><code>  
    permissions:
      id-token: write  # This is required for requesting the JWT
</code></pre>

### Continuação do Job de Deploy

- **Download artifact from build job:** Se houver um artefato (como um zip com o código), este passo faz o download dele.

<pre><code>  
    steps:
      # Download artifact from build job (if you decide to create a zip for deployment)
      - name: Download artifact from build job
        uses: actions/download-artifact@v4
        with:
          name: python-app
</code></pre>

- **Unzip artifact for deployment:** Descompacta o artefato para preparar a implantação.

<pre><code>  
      # Unzip artifact for deployment
      - name: Unzip artifact for deployment
        run: unzip release.zip
</code></pre>

- **Login to Azure:** Realiza o login na conta do Azure usando credenciais seguras armazenadas nos segredos do repositório.

<pre><code> 
      # Login to Azure
      - name: Login to Azure
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZUREAPPSERVICE_CLIENTID_CBF2DD4C72E24359BE3D9CABF42BB682 }}
          tenant-id: ${{ secrets.AZUREAPPSERVICE_TENANTID_647D3E3A46B345479034447ED32C0767 }}
          subscription-id: ${{ secrets.AZUREAPPSERVICE_SUBSCRIPTIONID_E28204BC8E78421ABF9E700E60BB7F35 }}
</code></pre>

- **Deploy to Azure Web App:** Utiliza a ação de implantação do Azure para implantar a aplicação na Azure Web App especificada.

<pre><code> 
      # Deploy to Azure Web App
      - name: 'Deploy to Azure Web App'
        uses: azure/webapps-deploy@v3
        id: deploy-to-webapp
        with:
          app-name: 'quarksia'
          slot-name: 'Production'
</code></pre>

## Resumo do Funcionamento do Pipeline

- **Commits em branches que não são a main:**
  - Executam apenas o job de build, que inclui verificar o código, configurar o Python, instalar dependências, rodar testes e gerar relatórios.
  - Não há execução do job de deploy.

- **Pull Requests para a branch main:**
  - Executam o job de build conforme descrito, e se todos os testes passarem, o job de deploy será acionado (porque a condição `if: github.ref == 'refs/heads/main'` será verdadeira).
  - Portanto, a mesclagem para a branch main aciona tanto CI quanto CD.