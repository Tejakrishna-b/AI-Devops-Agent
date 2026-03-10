#!/usr/bin/env python3
"""
AI DevOps Agent - Interactive Web UI
Author: AI DevOps Team
"""

import streamlit as st
import sys
import os
import json
import requests
import yaml
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Page configuration
st.set_page_config(
    page_title="AI DevOps Agent - Professional Automation Platform",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Clean and Professional Theme
st.markdown("""
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main Container */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header Styles */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        font-size: 1.1rem;
        font-weight: 400;
        color: #6c757d;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Card Styles */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
    }
    
    /* Step Container */
    .step-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .step-content {
        background: white;
        padding: 1.5rem;
        border-radius: 0 0 8px 8px;
        border: 1px solid #e9ecef;
        border-top: none;
    }
    
    /* Status Badges */
    .badge-completed {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .badge-progress {
        background-color: #ffc107;
        color: #000;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .badge-pending {
        background-color: #6c757d;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Button Styles */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Code Block Styling */
    code {
        background-color: #f8f9fa;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #e83e8c;
    }
    
    pre {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #667eea;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #1a1a2e;
    }
    
    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.25rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 1.25rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 1.25rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    
    /* Input Fields */
    .stTextInput input {
        border-radius: 6px;
        border: 2px solid #e9ecef;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Remove default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: white;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        font-weight: 500;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a2e;
    }
</style>
""", unsafe_allow_html=True)

class AIDevOpsAgentUI:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load configuration from config.yaml"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            self.jira_url = config["jira"]["url"]
            self.jira_username = config["jira"]["username"]
            self.jira_token = config["jira"]["api_token"]
            self.git_owner = config["git"]["owner"]
            self.git_repo = config["git"]["repo"]
            self.github_url = f"https://github.com/{self.git_owner}/{self.git_repo}"
        except Exception as e:
            st.error(f"❌ Failed to load configuration: {str(e)}")
            self.jira_url = None
    
    def fetch_jira_ticket(self, issue_key):
        """Fetch Jira ticket details"""
        try:
            url = f"{self.jira_url}/rest/api/2/issue/{issue_key}"
            auth = (self.jira_username, self.jira_token)
            response = requests.get(url, auth=auth)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"❌ Failed to fetch Jira ticket: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return None
    
    def extract_requirements(self, fields):
        """Extract requirements from Jira ticket"""
        requirements = []
        summary = fields.get('summary', '').lower()
        description = fields.get('description', '').lower()
        full_text = f"{summary} {description}"
        
        # Pattern matching for specific requirements
        if any(word in full_text for word in ['upgrade', 'update', 'migrate']):
            if 'java' in full_text:
                requirements.append("Upgrade Java version")
            if 'sonarqube' in full_text or 'sonar' in full_text:
                requirements.append("Upgrade SonarQube")
            if 'python' in full_text:
                requirements.append("Upgrade Python version")
            if 'node' in full_text:
                requirements.append("Upgrade Node.js version")
        
        if 'automate' in full_text:
            requirements.append("Automate manual processes")
        if 'terraform' in full_text or 'infrastructure' in full_text:
            requirements.append("Provision infrastructure with Terraform")
        if 'ci/cd' in full_text or 'pipeline' in full_text:
            requirements.append("Update CI/CD pipelines")
        if 'docker' in full_text or 'container' in full_text:
            requirements.append("Update Docker configurations")
        
        if not requirements:
            requirements.append(f"{fields.get('summary', 'Implement requested changes')}")
        
        return requirements
    
    def generate_technical_commands(self, task_type):
        """Generate real DevOps commands based on task type"""
        commands = {}
        
        if 'java' in task_type.lower():
            commands = {
                "backup": "tar -czf backup-$(date +%Y%m%d).tar.gz src/ pom.xml",
                "maven_update": "mvn versions:set-property -Dproperty=maven.compiler.source -DnewVersion=21\nmvn versions:set-property -Dproperty=maven.compiler.target -DnewVersion=21",
                "gradle_update": "sed -i 's/sourceCompatibility = \"18\"/sourceCompatibility = \"21\"/' build.gradle",
                "docker": "FROM eclipse-temurin:21-jdk-alpine",
                "test": "mvn clean test -Dmaven.compiler.release=21",
                "build": "mvn clean package -DskipTests"
            }
        elif 'sonarqube' in task_type.lower():
            commands = {
                "backup": "docker exec sonarqube pg_dump -U sonar > sonarqube_backup.sql",
                "download": "wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-10.2.zip",
                "terraform": "terraform plan -out=sonarqube.tfplan\nterraform apply sonarqube.tfplan",
                "health_check": "curl http://localhost:9000/api/system/health",
                "restart": "docker-compose down && docker-compose up -d"
            }
        elif 'python' in task_type.lower():
            commands = {
                "venv": "python3.12 -m venv venv\nsource venv/bin/activate",
                "requirements": "pip install --upgrade pip\npip install -r requirements.txt",
                "test": "pytest tests/ -v --cov",
                "docker": "FROM python:3.12-slim"
            }
        elif 'terraform' in task_type.lower():
            commands = {
                "init": "terraform init -upgrade",
                "validate": "terraform validate && terraform fmt -check",
                "plan": "terraform plan -out=tfplan",
                "apply": "terraform apply tfplan",
                "destroy": "terraform destroy -auto-approve"
            }
        elif 'kubernetes' in task_type.lower() or 'k8s' in task_type.lower():
            commands = {
                "deploy": "kubectl apply -f k8s/ --namespace=production",
                "rollout": "kubectl rollout status deployment/app-deployment",
                "logs": "kubectl logs -f deployment/app-deployment --tail=100",
                "scale": "kubectl scale deployment app-deployment --replicas=3"
            }
        
        return commands
    
    def generate_solution_steps(self, issue_data):
        """Generate realistic, technical DevOps solution steps"""
        fields = issue_data.get('fields', {})
        requirements = self.extract_requirements(fields)
        summary = fields.get('summary', '').lower()
        description = fields.get('description', '').lower()
        full_text = f"{summary} {description}"
        
        steps = []
        
        # Step 1: Environment Analysis & Prerequisites
        prereq_checks = []
        if 'java' in full_text:
            prereq_checks = [
                "✓ Check current Java version: `java -version`",
                "✓ Verify JAVA_HOME: `echo $JAVA_HOME`",
                "✓ Check Maven/Gradle version: `mvn -version` or `gradle -v`",
                "✓ Backup current configuration: `git stash && git pull`",
                "✓ Ensure CI/CD pipeline supports Java 21"
            ]
        elif 'sonarqube' in full_text:
            prereq_checks = [
                "✓ Check current SonarQube version: `curl localhost:9000/api/system/status`",
                "✓ Verify database backup: `pg_dump -U sonar sonarqube > backup.sql`",
                "✓ Check disk space: `df -h`",
                "✓ Review system requirements for new version",
                "✓ Plan maintenance window (downtime required)"
            ]
        elif 'terraform' in full_text or 'infrastructure' in full_text:
            prereq_checks = [
                "✓ Check Terraform version: `terraform version`",
                "✓ Verify AWS CLI credentials: `aws sts get-caller-identity`",
                "✓ Review current infrastructure: `terraform state list`",
                "✓ Initialize backend: `terraform init -backend-config=prod.tfbackend`",
                "✓ Check for drift: `terraform plan -refresh-only`"
            ]
        else:
            prereq_checks = [
                "✓ Review current system architecture",
                "✓ Check dependencies and versions",
                "✓ Verify access to required systems",
                "✓ Create backup of current state"
            ]
        
        steps.append({
            "title": "Environment Analysis & Prerequisites",
            "description": "Validate environment and check prerequisites",
            "details": prereq_checks,
            "commands": prereq_checks,
            "status": "completed"
        })
        
        # Step 2: Technical Implementation Plan
        impl_plan = []
        code_changes = []
        
        if 'java' in full_text:
            impl_plan = [
                "📝 Update pom.xml: Change <java.version>18</java.version> to 21",
                "📝 Update build.gradle: sourceCompatibility = '21', targetCompatibility = '21'",
                "🐳 Update Dockerfile: FROM eclipse-temurin:21-jdk-alpine",
                "⚙️ Update CI/CD: Modify Jenkins/GitLab CI to use Java 21 image",
                "🔧 Update application.properties: Review removed/deprecated features",
                "🧪 Update test configurations for Java 21 compatibility"
            ]
            commands = self.generate_technical_commands('java')
            code_changes = [
                f"**Maven (pom.xml)**:\n```xml\n<properties>\n    <maven.compiler.source>21</maven.compiler.source>\n    <maven.compiler.target>21</maven.compiler.target>\n</properties>\n```",
                f"**Gradle (build.gradle)**:\n```gradle\njava {{\n    sourceCompatibility = '21'\n    targetCompatibility = '21'\n}}\n```",
                f"**Dockerfile**:\n```dockerfile\n{commands.get('docker', '')}\nWORKDIR /app\nCOPY target/*.jar app.jar\nENTRYPOINT [\"java\", \"-jar\", \"app.jar\"]\n```"
            ]
        elif 'sonarqube' in full_text:
            impl_plan = [
                "💾 Backup current SonarQube database and plugins",
                "🏗️ Create Terraform module for SonarQube 10.2 infrastructure",
                "🐳 Update docker-compose.yml with new SonarQube image",
                "📊 Migrate quality profiles and rules to new version",
                "🔐 Update LDAP/SAML authentication configuration",
                "🔄 Update CI/CD scanner plugin versions"
            ]
            commands = self.generate_technical_commands('sonarqube')
            code_changes = [
                f"**Terraform (sonarqube.tf)**:\n```hcl\nresource \"aws_ecs_task_definition\" \"sonarqube\" {{\n  family = \"sonarqube\"\n  container_definitions = jsonencode([{{\n    name  = \"sonarqube\"\n    image = \"sonarqube:10.2-community\"\n    portMappings = [{{ containerPort = 9000 }}]\n  }}])\n}}\n```",
                f"**Docker Compose**:\n```yaml\nservices:\n  sonarqube:\n    image: sonarqube:10.2-community\n    ports:\n      - \"9000:9000\"\n    environment:\n      - SONAR_JDBC_URL=jdbc:postgresql://db:5432/sonar\n```"
            ]
        elif 'terraform' in full_text or 'infrastructure' in full_text:
            impl_plan = [
                "🏗️ Create Terraform modules: VPC, EC2, RDS, S3",
                "📝 Define variables.tf with all configurable parameters",
                "🔐 Setup backend.tf for remote state (S3 + DynamoDB)",
                "🌍 Create environment-specific .tfvars files",
                "📊 Add outputs.tf for resource information",
                "🔒 Implement security groups and IAM policies"
            ]
            commands = self.generate_technical_commands('terraform')
            code_changes = [
                f"**VPC Module (vpc.tf)**:\n```hcl\nresource \"aws_vpc\" \"main\" {{\n  cidr_block           = var.vpc_cidr\n  enable_dns_hostnames = true\n  enable_dns_support   = true\n  tags = {{\n    Name = \"${{var.environment}}-vpc\"\n  }}\n}}\n```",
                f"**Backend Config (backend.tf)**:\n```hcl\nterraform {{\n  backend \"s3\" {{\n    bucket         = \"terraform-state-bucket\"\n    key            = \"prod/terraform.tfstate\"\n    region         = \"us-east-1\"\n    dynamodb_table = \"terraform-locks\"\n  }}\n}}\n```"
            ]
        else:
            impl_plan = requirements
            code_changes = ["Implementation will vary based on specific requirements"]
        
        steps.append({
            "title": "Technical Implementation Plan",
            "description": "Detailed code changes and configurations required",
            "details": impl_plan,
            "commands": code_changes,
            "status": "in_progress"
        })
        
        # Step 3: Execute Changes with CLI Commands
        cli_commands = []
        commands_dict = self.generate_technical_commands(full_text)
        
        if 'java' in full_text:
            cli_commands = [
                f"**1. Backup Project**\n```bash\n{commands_dict.get('backup', 'tar -czf backup.tar.gz .')}\n```",
                f"**2. Update Maven**\n```bash\n{commands_dict.get('maven_update', 'mvn versions:update-properties')}\n```",
                f"**3. Build Project**\n```bash\n{commands_dict.get('build', 'mvn clean package')}\n```",
                f"**4. Run Tests**\n```bash\n{commands_dict.get('test', 'mvn test')}\n```",
                "**5. Update Docker Image**\n```bash\ndocker build -t myapp:java21 .\ndocker push myapp:java21\n```"
            ]
        elif 'sonarqube' in full_text:
            cli_commands = [
                f"**1. Backup Database**\n```bash\n{commands_dict.get('backup', 'docker exec sonarqube pg_dump')}\n```",
                f"**2. Apply Terraform**\n```bash\n{commands_dict.get('terraform', 'terraform apply')}\n```",
                f"**3. Health Check**\n```bash\n{commands_dict.get('health_check', 'curl localhost:9000/api/system/health')}\n```",
                "**4. Migrate Data**\n```bash\ncurl -u admin:admin -X POST http://localhost:9000/api/system/migrate_db\n```"
            ]
        elif 'terraform' in full_text:
            cli_commands = [
                f"**1. Initialize Terraform**\n```bash\n{commands_dict.get('init', 'terraform init')}\n```",
                f"**2. Validate Config**\n```bash\n{commands_dict.get('validate', 'terraform validate')}\n```",
                f"**3. Plan Changes**\n```bash\n{commands_dict.get('plan', 'terraform plan')}\n```",
                f"**4. Apply Infrastructure**\n```bash\n{commands_dict.get('apply', 'terraform apply')}\n```",
                "**5. Verify Resources**\n```bash\nterraform state list\nterraform output\n```"
            ]
        else:
            cli_commands = [
                "Commands will be generated based on specific task requirements",
                "Check generated workspace files for detailed scripts"
            ]
        
        steps.append({
            "title": "Execute Changes (CLI Commands)",
            "description": "Real commands to run on your terminal",
            "details": cli_commands,
            "commands": cli_commands,
            "status": "pending"
        })
        
        # Step 4: CI/CD Pipeline Updates
        cicd_updates = []
        
        if 'java' in full_text:
            cicd_updates = [
                "**Jenkins Pipeline**:\n```groovy\npipeline {\n  agent { docker { image 'maven:3.9-eclipse-temurin-21' } }\n  stages {\n    stage('Build') { steps { sh 'mvn clean package' } }\n    stage('Test') { steps { sh 'mvn test' } }\n  }\n}\n```",
                "**GitHub Actions**:\n```yaml\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/setup-java@v3\n        with:\n          java-version: '21'\n          distribution: 'temurin'\n```",
                "**GitLab CI**:\n```yaml\nimage: maven:3.9-eclipse-temurin-21\nbuild:\n  script:\n    - mvn clean package\n```"
            ]
        elif 'sonarqube' in full_text:
            cicd_updates = [
                "**Update Scanner Version**:\n```yaml\nsonar-scanner:\n  image: sonarsource/sonar-scanner-cli:5.0\n  script:\n    - sonar-scanner -Dsonar.host.url=$SONAR_URL\n```",
                "**Update Quality Gate**:\n```bash\ncurl -u admin:admin -X POST 'http://sonarqube:9000/api/qualitygates/create?name=MyGate'\n```"
            ]
        elif 'terraform' in full_text:
            cicd_updates = [
                "**Terraform CI/CD Pipeline**:\n```yaml\nterraform-plan:\n  stage: plan\n  script:\n    - terraform init\n    - terraform plan -out=tfplan\n  artifacts:\n    paths: [tfplan]\n\nterraform-apply:\n  stage: apply\n  script:\n    - terraform apply tfplan\n  when: manual\n```"
            ]
        else:
            cicd_updates = ["Update CI/CD pipelines based on changes made"]
        
        steps.append({
            "title": "CI/CD Pipeline Configuration",
            "description": "Update automated build and deployment pipelines",
            "details": cicd_updates,
            "commands": cicd_updates,
            "status": "pending"
        })
        
        # Step 5: Testing & Validation
        test_commands = []
        
        if 'java' in full_text:
            test_commands = [
                "**Unit Tests**: `mvn test -Dtest=**/*Test.java`",
                "**Integration Tests**: `mvn verify -P integration-tests`",
                "**Code Coverage**: `mvn jacoco:report && open target/site/jacoco/index.html`",
                "**SonarQube Scan**: `mvn sonar:sonar -Dsonar.host.url=$SONAR_URL`",
                "**Performance Test**: `jmeter -n -t load-test.jmx -l results.jtl`"
            ]
        elif 'sonarqube' in full_text:
            test_commands = [
                "**Health Check**: `curl http://localhost:9000/api/system/health`",
                "**Database Connection**: `curl http://localhost:9000/api/system/db_migration_status`",
                "**Plugin Compatibility**: Check SonarQube admin panel > Plugins",
                "**Run Sample Analysis**: `sonar-scanner -Dsonar.projectKey=test`"
            ]
        elif 'terraform' in full_text:
            test_commands = [
                "**Validate Syntax**: `terraform validate`",
                "**Format Check**: `terraform fmt -check -recursive`",
                "**Security Scan**: `tfsec . --concise-output`",
                "**Cost Estimate**: `infracost breakdown --path .`",
                "**Compliance Check**: `checkov -d . --framework terraform`"
            ]
        else:
            test_commands = [
                "Execute comprehensive tests",
                "Validate in staging environment",
                "Monitor system metrics"
            ]
        
        steps.append({
            "title": "Testing & Validation",
            "description": "Comprehensive testing before production deployment",
            "details": test_commands,
            "commands": test_commands,
            "status": "pending"
        })
        
        # Step 6: Deployment Strategy
        deployment_steps = []
        
        if 'java' in full_text or 'sonarqube' in full_text:
            deployment_steps = [
                "**Blue-Green Deployment**:\n```bash\n# Deploy to green environment\nkubectl apply -f k8s/green/ --namespace=production\n# Switch traffic\nkubectl patch service app-service -p '{\"spec\":{\"selector\":{\"version\":\"green\"}}}'\n# Monitor for 10 minutes\n# Rollback if needed\nkubectl patch service app-service -p '{\"spec\":{\"selector\":{\"version\":\"blue\"}}}'\n```",
                "**Canary Deployment**:\n```yaml\napiVersion: flagger.app/v1beta1\nkind: Canary\nmetadata:\n  name: app-canary\nspec:\n  targetRef:\n    apiVersion: apps/v1\n    kind: Deployment\n    name: app\n  progressDeadlineSeconds: 300\n  service:\n    port: 8080\n  analysis:\n    interval: 1m\n    threshold: 5\n    stepWeight: 10\n```",
                "**Monitoring Commands**:\n```bash\n# Check pod status\nkubectl get pods -n production -w\n# View logs\nkubectl logs -f deployment/app --tail=100\n# Check metrics\nkubectl top pods -n production\n```"
            ]
        elif 'terraform' in full_text:
            deployment_steps = [
                "**1. Plan & Review**:\n```bash\nterraform plan -out=prod.tfplan\n# Review plan thoroughly\n```",
                "**2. Apply with Confirmation**:\n```bash\nterraform apply prod.tfplan\n```",
                "**3. Verify Resources**:\n```bash\naws ec2 describe-instances --filters \"Name=tag:Environment,Values=production\"\n```",
                "**4. Update Monitoring**:\n```bash\n# Add CloudWatch alarms\naws cloudwatch put-metric-alarm --alarm-name high-cpu --metric-name CPUUtilization\n```"
            ]
        else:
            deployment_steps = [
                "Deploy to staging first",
                "Run smoke tests",
                "Deploy to production with monitoring",
                "Verify deployment success"
            ]
        
        steps.append({
            "title": "Production Deployment",
            "description": "Safe deployment strategy with rollback plan",
            "details": deployment_steps,
            "commands": deployment_steps,
            "status": "pending"
        })
        
        # Step 7: Monitoring & Rollback Plan
        monitoring_setup = [
            "**Application Monitoring**:\n```bash\n# Prometheus metrics\ncurl http://localhost:8080/actuator/prometheus\n# Grafana dashboard\nopen http://grafana:3000/d/app-dashboard\n```",
            "**Log Aggregation**:\n```bash\n# View logs in ELK\nkibana: host:5601 index:app-logs-*\n# Or Cloudwatch\naws logs tail /aws/ecs/app-production --follow\n```",
            "**Alerting Setup**:\n```yaml\napiVersion: monitoring.coreos.com/v1\nkind: PrometheusRule\nmetadata:\n  name: app-alerts\nspec:\n  groups:\n    - name: app\n      rules:\n        - alert: HighErrorRate\n          expr: rate(http_requests_total{status=~\"5..\"}[5m]) > 0.05\n```",
            "**Rollback Commands**:\n```bash\n# Kubernetes rollback\nkubectl rollout undo deployment/app-deployment\n# Docker rollback\ndocker service update --rollback app-service\n# Terraform rollback\nterraform apply -var-file=previous-state.tfvars\n```",
            "**Health Checks**:\n```bash\n# Endpoint health\nwatch -n 5 'curl -s http://app/health | jq'\n# System metrics\nkubectl top nodes && kubectl top pods\n```"
        ]
        
        steps.append({
            "title": "Monitoring & Rollback Strategy",
            "description": "Continuous monitoring with rollback procedures",
            "details": monitoring_setup,
            "commands": monitoring_setup,
            "status": "pending"
        })
        
        return steps

def main():
    # Header
    st.markdown('<h1 class="main-header">AI DevOps Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Professional DevOps Automation & Infrastructure Management Platform</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize agent
    agent = AIDevOpsAgentUI()
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        st.info(f"**GitHub Repository**\n{agent.github_url}")
        st.info(f"**Jira Instance**\n{agent.jira_url}")
        
        st.markdown("---")
        st.header("�️ DevOps Skills")
        st.markdown("""
        **Infrastructure:**
        - ☁️ Terraform (AWS, Azure, GCP)
        - 🐳 Docker & Docker Compose
        - ☸️ Kubernetes (K8s)
        - 🏗️ Infrastructure as Code
        
        **CI/CD:**
        - ⚙️ Jenkins, GitLab CI, GitHub Actions
        - 🔄 Blue-Green Deployments
        - 🐤 Canary Deployments
        - 📊 ArgoCD, Flux
        
        **Languages & Build:**
        - ☕ Java (Maven, Gradle)
        - 🐍 Python (pip, venv)
        - 🟢 Node.js (npm, yarn)
        - 🔵 .NET (NuGet)
        
        **Monitoring & Security:**
        - 📈 Prometheus, Grafana
        - 📝 ELK Stack, CloudWatch
        - 🔍 SonarQube
        - 🔐 Security Scanning (tfsec, checkov)
        
        **Cloud Platforms:**
        - ☁️ AWS (EC2, ECS, Lambda, S3)
        - 🔵 Azure (VMs, AKS, Functions)
        - 🟡 GCP (GCE, GKE)
        """)
        
        st.markdown("---")
        st.header("Quick Access")
        st.markdown(f"[GitHub Repository]({agent.github_url})")
        st.markdown(f"[Workspace Files]({agent.github_url}/tree/main/workspace)")
        st.markdown(f"[Pull Requests]({agent.github_url}/pulls)")

    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Enter Jira Ticket")
        jira_input = st.text_input(
            "Jira Ticket Number",
            placeholder="e.g., STBBS-649, DEV-123, PROJ-456",
            help="Enter the Jira ticket ID for automated analysis and solution generation"
        )
    
    with col2:
        st.subheader("Action")
        analyze_button = st.button("Analyze Ticket", type="primary", use_container_width=True)
    
    # Process when button clicked
    if analyze_button and jira_input:
        with st.spinner(f"Fetching Jira ticket {jira_input}..."):
            issue_data = agent.fetch_jira_ticket(jira_input.strip())
        
        if issue_data:
            fields = issue_data.get('fields', {})
            issue_key = issue_data.get('key', jira_input)
            
            # Display ticket info
            st.success(f"Successfully fetched ticket: **{issue_key}**")
            st.markdown("---")
            
            # Ticket Details
            st.header("Ticket Details")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ticket ID", issue_key)
            with col2:
                st.metric("Priority", fields.get('priority', {}).get('name', 'N/A'))
            with col3:
                st.metric("Status", fields.get('status', {}).get('name', 'N/A'))
            
            st.markdown(f"**Summary:** {fields.get('summary', 'N/A')}")
            st.markdown(f"**Type:** {fields.get('issuetype', {}).get('name', 'N/A')}")
            
            if fields.get('description'):
                with st.expander("View Full Description"):
                    st.write(fields.get('description'))
            
            st.markdown("---")
            
            # Generate and display solution steps
            st.header("Technical DevOps Solution")
            st.info("**Production-ready implementation steps with executable commands**")
            steps = agent.generate_solution_steps(issue_data)
            
            for idx, step in enumerate(steps, 1):
                status_badge = {
                    "completed": "[COMPLETED]",
                    "in_progress": "[IN PROGRESS]",
                    "pending": "[PENDING]"
                }.get(step['status'], "[PENDING]")
                
                with st.expander(f"{status_badge} **Step {idx}: {step['title']}**", expanded=(idx <= 2)):
                    st.write(f"**{step['description']}**")
                    st.markdown("---")
                    
                    # Display details/commands
                    if 'commands' in step and step['commands']:
                        for cmd in step['commands']:
                            if '```' in cmd:
                                # It's a code block, render as markdown
                                st.markdown(cmd)
                            else:
                                # Regular text
                                st.markdown(f"{cmd}")
                    else:
                        for detail in step['details']:
                            st.markdown(f"- {detail}")
            
            st.markdown("---")
            
            # Action buttons
            st.header("Execute Automation")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Run Agent", type="primary", use_container_width=True):
                    st.info("Running automation agent...")
                    st.code(f'python3 src/main.py "jira: {issue_key}"', language="bash")
                    st.warning("To execute, run this command in your terminal")
            
            with col2:
                branch_name = f"feature/{issue_key.lower()}"
                github_link = f"{agent.github_url}/tree/{branch_name}"
                st.link_button("View Branch", github_link, use_container_width=True)
            
            with col3:
                pr_link = f"{agent.github_url}/pulls"
                st.link_button("View PRs", pr_link, use_container_width=True)
            
            # GitHub workspace link
            st.markdown("---")
            st.info(f"""
            **Workspace Files:** All generated files will be available at:
            
            `{agent.github_url}/tree/main/workspace`
            
            **Generated Branch:** `{branch_name}`
            """)
    
    elif analyze_button and not jira_input:
        st.warning("Please enter a Jira ticket number")
    
    # Quick examples
    if not analyze_button:
        st.markdown("---")
        st.header("Agent Capabilities")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("""
            **Software Upgrades**
            - Real Maven/Gradle configs
            - Dockerfile updates
            - CI/CD pipeline changes  
            - Testing commands
            - Deployment strategies
            """)
        
        with col2:
            st.success("""
            **Infrastructure Provisioning**
            - Terraform modules (VPC, EC2, RDS)
            - Kubernetes manifests
            - Security groups & IAM
            - Cost optimization
            - Monitoring setup
            """)
        
        with col3:
            st.success("""
            **CI/CD Automation**
            - Jenkins/GitLab/GitHub Actions
            - Blue-Green deployments
            - Canary releases
            - Rollback procedures
            - Health check automation
            """)

if __name__ == "__main__":
    main()
