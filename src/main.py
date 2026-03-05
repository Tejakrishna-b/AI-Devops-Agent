#!/usr/bin/env python3
"""
AI DevOps Agent - Improved Version
Generates REAL, task-specific solutions based on actual requirements
"""

import sys
import os
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime

class AIDevOpsAgent:
    def __init__(self):
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.jira_url = config["jira"]["url"]
        self.jira_username = config["jira"]["username"]
        self.jira_token = config["jira"]["api_token"]
        self.git_provider = config["git"]["provider"]
        self.git_repo = config["git"]["repo"]
        self.git_token = config["git"].get("token")
        self.git_owner = config["git"].get("owner")
        self.sonarqube_url = config["sonarqube"]["url"]
        self.sonarqube_token = config["sonarqube"]["token"]

    def get_jira_issue(self, issue_key):
        """Fetch Jira ticket details"""
        import requests
        url = f"{self.jira_url}/rest/api/2/issue/{issue_key}"
        auth = (self.jira_username, self.jira_token)
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to fetch Jira issue: {response.text}")
            return None

    def explain_jira_issue(self, issue_data):
        """Explain Jira issue in detail before proceeding"""
        if not issue_data:
            return {"summary": "", "description": "", "requirements": []}
        
        print("\n" + "="*70)
        print("📋 JIRA TICKET ANALYSIS")
        print("="*70)
        
        fields = issue_data.get("fields", {})
        issue_key = issue_data.get("key", "Unknown")
        
        print(f"\n🎫 Ticket ID: {issue_key}")
        print(f"📌 Summary: {fields.get('summary', 'N/A')}")
        print(f"🏷️  Type: {fields.get('issuetype', {}).get('name', 'N/A')}")
        print(f"⚠️  Priority: {fields.get('priority', {}).get('name', 'N/A')}")
        print(f"📊 Status: {fields.get('status', {}).get('name', 'N/A')}")
        
        description = fields.get('description', '')
        if description:
            print(f"\n📝 Description:\n{description[:500]}..." if len(description) > 500 else f"\n📝 Description:\n{description}")
        
        # Extract meaningful requirements
        requirements = self.extract_requirements_from_jira(fields)
        print("\n🎯 Identified Requirements:")
        for i, req in enumerate(requirements, 1):
            print(f"   {i}. {req}")
        
        print("\n" + "="*70)
        print("🚀 PROCEEDING WITH AUTOMATED WORKFLOW")
        print("="*70 + "\n")
        
        return {
            "summary": fields.get('summary', ''),
            "description": description,
            "requirements": requirements,
            "issue_key": issue_key
        }

    def extract_requirements_from_jira(self, fields):
        """Extract real requirements from Jira ticket"""
        requirements = []
        summary = fields.get('summary', '').lower()
        description = fields.get('description', '').lower()
        full_text = f"{summary} {description}"
        
        # Pattern matching for specific requirements
        if 'solution' in full_text and 'report' in full_text:
            requirements.append("Automate solution reporting with unified format")
        if 'centralized' in full_text and 'config' in full_text:
            requirements.append("Create centralized configuration management system")
        if 'duplicate' in full_text:
            requirements.append("Eliminate duplicate configurations")
        if 'automate' in full_text:
            requirements.append("Automate manual processes")
        
        # Default if no specific patterns
        if not requirements:
            requirements.append(f"Implement: {fields.get('summary', 'Requested changes')}")
        
        return requirements

    def analyze_prompt(self, prompt):
        """Analyze user prompt to determine the actual task"""
        print(f"🔍 Analyzing prompt: {prompt}\n")
        
        # Check for Jira reference
        if "jira:" in prompt.lower():
            issue_key = prompt.split("jira:")[1].strip()
            return {"type": "jira", "issue_key": issue_key}
        
        # Detect Java upgrade
        java_match = re.search(r'(upgrade|update|migrate).*java.*(?:from\s+(?:version\s+)?)([\d]+).*(?:to\s+(?:version\s+)?)([\d]+)', prompt, re.IGNORECASE)
        if java_match:
            from_version = java_match.group(2) if java_match.group(2) else "11"
            to_version = java_match.group(3) if java_match.group(3) else "21"
            return {
                "type": "java_upgrade",
                "from_version": from_version,
                "to_version": to_version,
                "software": "Java"
            }
        
        # Detect SonarQube upgrade
        if re.search(r'(upgrade|update).*sonarqube', prompt, re.IGNORECASE):
            version_match = re.search(r'version\s*(\d+\.\d+)', prompt)
            version = version_match.group(1) if version_match else "latest"
            return {
                "type": "sonarqube_upgrade",
                "version": version,
                "software": "SonarQube"
            }
        
        # Detect Python upgrade
        python_match = re.search(r'(upgrade|update|migrate).*python.*(?:from\s*)?([\d.]+).*(?:to\s*)?([\d.]+)', prompt, re.IGNORECASE)
        if python_match:
            from_version = python_match.group(2) if python_match.group(2) else "3.8"
            to_version = python_match.group(3) if python_match.group(3) else "3.12"
            return {
                "type": "python_upgrade",
                "from_version": from_version,
                "to_version": to_version,
                "software": "Python"
            }
        
        # Detect Node.js upgrade
        node_match = re.search(r'(upgrade|update|migrate).*(node|nodejs).*(?:from\s*)?([\d.]+).*(?:to\s*)?([\d.]+)', prompt, re.IGNORECASE)
        if node_match:
            from_version = node_match.group(3) if node_match.group(3) else "14"
            to_version = node_match.group(4) if node_match.group(4) else "20"
            return {
                "type": "node_upgrade",
                "from_version": from_version,
                "to_version": to_version,
                "software": "Node.js"
            }
        
        return {"type": "unknown", "prompt": prompt}

    def create_branch(self, task_info):
        """Create Git branch specific to the task"""
        if task_info["type"] == "jira":
            branch_name = f"feature/{task_info['issue_key'].lower()}"
        elif task_info["type"] == "java_upgrade":
            branch_name = f"feature/upgrade-java-{task_info['from_version']}-to-{task_info['to_version']}"
        elif task_info["type"] == "sonarqube_upgrade":
            branch_name = f"feature/upgrade-sonarqube-{task_info['version']}"
        elif task_info["type"] == "python_upgrade":
            branch_name = f"feature/upgrade-python-{task_info['from_version']}-to-{task_info['to_version']}"
        elif task_info["type"] == "node_upgrade":
            branch_name = f"feature/upgrade-nodejs-{task_info['from_version']}-to-{task_info['to_version']}"
        else:
            branch_name = f"feature/ai-agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        print(f"\n🌿 Creating Git branch: {branch_name}")
        
        try:
            # Check if branch exists
            result = subprocess.run(
                ["git", "rev-parse", "--verify", branch_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"   ⚠️  Branch {branch_name} already exists, checking it out...")
                subprocess.run(["git", "checkout", branch_name], check=True)
            else:
                subprocess.run(["git", "checkout", "-b", branch_name], check=True)
                print(f"   ✅ Created and checked out branch: {branch_name}")
            
            return branch_name
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to create branch: {e}")
            return None

    def create_workspace_for_task(self, task_info, branch_name):
        """Create task-specific workspace directory"""
        # Create workspace subdirectory for this specific task
        workspace_name = branch_name.replace('feature/', '').replace('/', '-')
        workspace_path = Path("workspace") / workspace_name
        workspace_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created task workspace: {workspace_path}")
        return workspace_path

    def generate_files_for_task(self, task_info, workspace_path):
        """Generate files based on the ACTUAL task requirements"""
        files_created = []
        
        if task_info["type"] == "java_upgrade":
            files_created = self.generate_java_upgrade_files(task_info, workspace_path)
        elif task_info["type"] == "sonarqube_upgrade":
            files_created = self.generate_sonarqube_upgrade_files(task_info, workspace_path)
        elif task_info["type"] == "python_upgrade":
            files_created = self.generate_python_upgrade_files(task_info, workspace_path)
        elif task_info["type"] == "node_upgrade":
            files_created = self.generate_node_upgrade_files(task_info, workspace_path)
        elif task_info["type"] == "jira":
            files_created = self.generate_jira_solution_files(task_info, workspace_path)
        else:
            print(f"⚠️  Unknown task type: {task_info['type']}")
        
        return files_created

    def generate_java_upgrade_files(self, task_info, workspace_path):
        """Generate REAL Java upgrade files with actual migration steps"""
        from_ver = task_info['from_version']
        to_ver = task_info['to_version']
        files = []
        
        print(f"\n⬆️  Generating Java {from_ver} → {to_ver} upgrade files...")
        
        # 1. Comprehensive Migration Guide
        guide_path = workspace_path / "JAVA_MIGRATION_GUIDE.md"
        with open(guide_path, "w") as f:
            f.write(f"""# Java {from_ver} to {to_ver} Migration Guide

## 🎯 Objective
Upgrade your Java project from version **{from_ver}** to **{to_ver}** with minimal downtime and risk.

## 📋 Pre-Migration Checklist

### 1. Environment Preparation
- [ ] Verify Java {to_ver} is installed
  ```bash
  java -version  # Should show: openjdk version "{to_ver}"
  ```
- [ ] Backup your project
  ```bash
  cp -r . ../project-backup-$(date +%Y%m%d)
  ```
- [ ] Review [Java {to_ver} Release Notes](https://openjdk.org/projects/jdk/{to_ver}/)
- [ ] Check library compatibility with Java {to_ver}

### 2. Dependency Analysis
Review your project dependencies for Java {to_ver} compatibility:
- Spring Boot: Requires 3.0+ for Java 17+
- Hibernate: Upgrade to 6.x for Java 17+
- JUnit: Use JUnit 5.x
- Check [Maven Central](https://search.maven.org/) for updated versions

## 🔧 Step-by-Step Migration

### Step 1: Update Maven Configuration (pom.xml)

**Find this:**
```xml
<properties>
    <maven.compiler.source>{from_ver}</maven.compiler.source>
    <maven.compiler.target>{from_ver}</maven.compiler.target>
</properties>
```

** Replace with:**
```xml
<properties>
    <maven.compiler.source>{to_ver}</maven.compiler.source>
    <maven.compiler.target>{to_ver}</maven.compiler.target>
    <java.version>{to_ver}</java.version>
</properties>
```

**Update compiler plugin:**
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.12.1</version>
    <configuration>
        <source>{to_ver}</source>
        <target>{to_ver}</target>
        <release>{to_ver}</release>
    </configuration>
</plugin>
```

### Step 2: Update Gradle Configuration (build.gradle)

**For Groovy DSL:**
```groovy
java {{
    sourceCompatibility = JavaVersion.VERSION_{to_ver}
    targetCompatibility = JavaVersion.VERSION_{to_ver}
    toolchain {{
        languageVersion = JavaLanguageVersion.of({to_ver})
    }}
}}
```

**For Kotlin DSL (build.gradle.kts):**
```kotlin
java {{
    sourceCompatibility = JavaVersion.VERSION_{to_ver}
    targetCompatibility = JavaVersion.VERSION_{to_ver}
}}
```

### Step 3: Update Dockerfile

**Old:**
```dockerfile
FROM openjdk:{from_ver}-jdk-alpine
```

**New:**
```dockerfile
FROM eclipse-temurin:{to_ver}-jdk-alpine AS build
# ... build stage ...

FROM eclipse-temurin:{to_ver}-jre-alpine
# ... runtime stage ...
```

### Step 4: Update CI/CD Pipeline

**GitHub Actions (.github/workflows/build.yml):**
```yaml
- name: Set up JDK {to_ver}
  uses: actions/setup-java@v4
  with:
    java-version: '{to_ver}'
    distribution: 'temurin'
```

**Jenkins (Jenkinsfile):**
```groovy
tools {{
    jdk 'JDK-{to_ver}'
}}
```

**GitLab CI (.gitlab-ci.yml):**
```yaml
image: eclipse-temurin:{to_ver}-jdk
```

### Step 5: Code Changes Required

#### Removed APIs (requires code changes):
""")
            
            # Add version-specific migration details
            if from_ver == "11" and to_ver in ["17", "21"]:
                f.write("""
**Security Manager (removed in Java 17+):**
```java
// OLD - No longer works
System.setSecuritymanager(new SecurityManager());

// NEW - Use alternative approaches
// Consider OS-level security, containers, or Java Platform Module System
```

**Nashorn JavaScript Engine (removed):**
```java
// OLD
ScriptEngine engine = new ScriptEngineManager().getEngineByName("nashorn");

// NEW - Use GraalVM JavaScript or other alternatives
```

**Applet API (removed):**
```java
// Applets are completely removed - migrate to web technologies
```
""")
            
            f.write("""
#### New Language Features You Can Use:

""")
            
            if to_ver >= "17":
                f.write("""
**Pattern Matching for instanceof (Java 16+):**
```java
// OLD
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.length());
}

// NEW
if (obj instanceof String s) {
    System.out.println(s.length());
}
```

**Records (Java 16+):**
```java
// OLD
public class Point {
    private final int x, y;
    public Point(int x, int y) { this.x = x; this.y = y; }
    public int x() { return x; }
    public int y() { return y; }
    // equals, hashCode, toString...
}

// NEW
public record Point(int x, int y) {}
```

**Sealed Classes (Java 17+):**
```java
public sealed interface Shape permits Circle, Rectangle, Square {}
public final class Circle implements Shape {}
public final class Rectangle implements Shape {}
public final class Square implements Shape {}
```
""")
            
            if to_ver >= "21":
                f.write("""
**Pattern Matching for switch (Java 21+):**
```java
// OLD
String formatted;
if (obj instanceof Integer i) {
    formatted = String.format("int %d", i);
} else if (obj instanceof Long l) {
    formatted = String.format("long %d", l);
} else {
    formatted = obj.toString();
}

// NEW
String formatted = switch (obj) {
    case Integer i -> String.format("int %d", i);
    case Long l -> String.format("long %d", l);
    case null -> "null";
    default -> obj.toString();
};
```

**Virtual Threads (Java 21):**
```java
// Create millions of lightweight threads
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> {
        executor.submit(() -> {
            // Your task here
        });
    });
}
```

**String Templates (Preview - Java 21):**
```java
// Available as preview feature
String name = "World";
String message = STR."Hello, \\{name}!";
```
""")
            
            f.write(f"""
## 🔨 Build and Test

### Clean Build
```bash
# Maven
mvn clean compile

# Gradle  
./gradlew clean build
```

### Run Tests
```bash
# Maven
mvn test

# Gradle
./gradlew test
```

### Fix Common Compilation Errors
```bash
# See detailed errors
mvn compile 2>&1 | tee compilation-errors.txt

# Search for deprecated API usage
grep -r "deprecated" src/
```

## 🐳 Docker Build

Update and test your Docker image:
```bash
# Build
docker build -t myapp:java{to_ver} .

# Test
docker run --rm myapp:java{to_ver}

# Compare size
docker images | grep myapp
```

## 🧪 Integration Testing

1. **Deploy to test environment**
2. **Run full test suite**
3. **Performance testing** - Java {to_ver} should be faster
4. **Monitor memory usage** - Check for any regressions

## 🚀 Deployment Strategy

### Option 1: Blue-Green Deployment
1. Deploy Java {to_ver} version alongside current
2. Gradually shift traffic
3. Monitor for issues
4. Complete cutover or rollback

### Option 2: Canary Deployment
1. Deploy to small percentage of servers
2. Monitor metrics (errors, latency, throughput)
3. Gradually increase deployment
4. Rollback if issues detected

## ⚠️ Common Issues & Solutions

### Issue: "java: invalid source release: {to_ver}"
**Solution:** Maven compiler plugin too old
```xml
<plugin>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.12.1</version> <!-- Must be 3.11.0+ -->
</plugin>
```

### Issue: "java.lang.UnsupportedClassVersionError"
**Solution:** Ensure runtime JVM is Java {to_ver}+
```bash
java -version  # Verify you're running {to_ver}
```

### Issue: "package javax.* does not exist"
**Solution:** Add Jakarta EE dependencies
```xml
<dependency>
    <groupId>jakarta.annotation</groupId>
    <artifactId>jakarta.annotation-api</artifactId>
    <version>2.1.1</version>
</dependency>
```

### Issue: Slow startup time
**Solution:** Enable Class Data Sharing (CDS)
```bash
# Create CDS archive
java -Xshare:dump

# Run with CDS
java -Xshare:on -jar myapp.jar
```

## ✅ Post-Migration Checklist

- [ ] All tests pass
- [ ] Application starts successfully
- [ ] API endpoints respond correctly
- [ ] Database connections work
- [ ] External integrations function
- [ ] Logging works as expected
- [ ] Monitoring/metrics are captured
- [ ] Performance meets SLAs
- [ ] No memory leaks detected
- [ ] Documentation updated

## 📚 Resources

- [Java {to_ver} Release Notes](https://openjdk.org/projects/jdk/{to_ver}/)
- [Java {to_ver} JEPs](https://openjdk.org/jeps/0)
- [Migration Guide](https://docs.oracle.com/en/java/javase/{to_ver}/migrate/)
- [Compatibility Guide](https://docs.oracle.com/en/java/javase/{to_ver}/compatibility/)

## 🔄 Rollback Plan

If migration fails:
```bash
# Restore from backup
rm -rf ./*
cp -r ../project-backup-* ./*

# Or use Git
git checkout <previous-commit-hash>

# Rebuild with old version
mvn clean install
```

---
**Generated by AI DevOps Agent**
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
        files.append(str(guide_path))
        print(f"   ✅ Created: {guide_path}")
        
        # 2. Automated Upgrade Script
        script_path = workspace_path / "upgrade_java.sh"
        with open(script_path, "w") as f:
            f.write(f"""#!/bin/bash
# Automated Java {from_ver} → {to_ver} Upgrade Script
# Generated by AI DevOps Agent

set -e  # Exit on error

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo -e "${{GREEN}}╔════════════════════════════════════════╗${{NC}}"
echo -e "${{GREEN}}║  Java {from_ver} → {to_ver} Upgrade Script  ║${{NC}}"
echo -e "${{GREEN}}╚════════════════════════════════════════╝${{NC}}"
echo ""

# Check if running with correct Java version
check_java_version() {{
    if command -v java &> /dev/null; then
        JAVA_VERSION=$(java -version 2>&1 | head -n 1 | awk -F '"' '{{print $2}}' | awk -F '.' '{{print $1}}')
        echo -e "Current Java version: ${{YELLOW}}$JAVA_VERSION${{NC}}"
        
        if [ "$JAVA_VERSION" != "{to_ver}" ]; then
            echo -e "${{YELLOW}}⚠️  Warning: Java {to_ver} not detected as default${{NC}}"
            echo "Please install Java {to_ver} and set JAVA_HOME:"
            echo ""
            echo "  # macOS (Homebrew)"
            echo "  brew install openjdk@{to_ver}"
            echo "  export JAVA_HOME=\\$(/usr/libexec/java_home -v {to_ver})"
            echo ""
            echo "  # Linux (Ubuntu/Debian)"
            echo "  sudo apt install openjdk-{to_ver}-jdk"
            echo "  export JAVA_HOME=/usr/lib/jvm/java-{to_ver}-openjdk-amd64"
            echo ""
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            echo -e "${{GREEN}}✅ Java {to_ver} detected${{NC}}"
        fi
    else
        echo -e "${{RED}}❌ Java not found!${{NC}}"
        exit 1
    fi
}}

# Create backup
create_backup() {{
    BACKUP_DIR="../java-{from_ver}-backup-$(date +%Y%m%d-%H%M%S)"
    echo -e "\\n${{YELLOW}}📦 Creating backup...${{NC}}"
    cp -r . "$BACKUP_DIR"
    echo -e "${{GREEN}}✅ Backup created: $BACKUP_DIR${{NC}}"
    echo "$BACKUP_DIR" > .java-upgrade-backup
}}

# Detect project type
detect_project_type() {{
    if [ -f "pom.xml" ]; then
        echo -e "\\n${{GREEN}}📋 Detected: Maven project${{NC}}"
        export PROJECT_TYPE="maven"
    elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
        echo -e "\\n${{GREEN}}📋 Detected: Gradle project${{NC}}"
        export PROJECT_TYPE="gradle"
    else
        echo -e "\\n${{YELLOW}}⚠️  No Maven or Gradle project detected${{NC}}"
        export PROJECT_TYPE="unknown"
    fi
}}

# Update Maven project
update_maven() {{
    echo -e "\\n${{YELLOW}}🔧 Updating Maven configuration...${{NC}}"
    
    # Backup pom.xml
    cp pom.xml pom.xml.backup
    
    # Update compiler source/target
    sed -i.bak 's/<maven\\.compiler\\.source>{from_ver}</<maven.compiler.source>{to_ver}</' pom.xml
    sed -i.bak 's/<maven\\.compiler\\.target>{from_ver}</<maven.compiler.target>{to_ver}</' pom.xml
    sed -i.bak 's/<java\\.version>{from_ver}</<java.version>{to_ver}</' pom.xml
    
    # Update compiler plugin
    if ! grep -q "maven-compiler-plugin.*3\\.1[1-9]" pom.xml; then
        echo -e "${{YELLOW}}⚠️  Consider updating maven-compiler-plugin to 3.12.1${{NC}}"
    fi
    
    rm -f pom.xml.bak
    echo -e "${{GREEN}}✅ Updated pom.xml${{NC}}"
    
    # Show changes
    echo -e "\\n${{YELLOW}}Changes made:${{NC}}"
    diff -u pom.xml.backup pom.xml || true
}}

# Update Gradle project
update_gradle() {{
    echo -e "\\n${{YELLOW}}🔧 Updating Gradle configuration...${{NC}}"
    
    GRADLE_FILE="build.gradle"
    if [ -f "build.gradle.kts" ]; then
        GRADLE_FILE="build.gradle.kts"
    fi
    
    # Backup
    cp "$GRADLE_FILE" "${{GRADLE_FILE}}.backup"
    
    # Update Java version
    sed -i.bak "s/sourceCompatibility.*=.*/sourceCompatibility = JavaVersion.VERSION_{to_ver}/" "$GRADLE_FILE"
    sed -i.bak "s/targetCompatibility.*=.*/targetCompatibility = JavaVersion.VERSION_{to_ver}/" "$GRADLE_FILE"
    sed -i.bak "s/languageVersion.*=.*JavaLanguageVersion\\.of([0-9]*)/languageVersion = JavaLanguageVersion.of({to_ver})/" "$GRADLE_FILE"
    
    rm -f "${{GRADLE_FILE}}.bak"
    echo -e "${{GREEN}}✅ Updated $GRADLE_FILE${{NC}}"
    
    # Show changes
    echo -e "\\n${{YELLOW}}Changes made:${{NC}}"
    diff -u "${{GRADLE_FILE}}.backup" "$GRADLE_FILE" || true
}}

# Update Dockerfile
update_dockerfile() {{
    if [ -f "Dockerfile" ]; then
        echo -e "\\n${{YELLOW}}🐳 Updating Dockerfile...${{NC}}"
        
        cp Dockerfile Dockerfile.backup
        
        # Update base images
        sed -i.bak "s/openjdk:{from_ver}/eclipse-temurin:{to_ver}/g" Dockerfile
        sed -i.bak "s/openjdk-{from_ver}/openjdk-{to_ver}/g" Dockerfile
        sed -i.bak "s/java-{from_ver}/java-{to_ver}/g" Dockerfile
        
        rm -f Dockerfile.bak
        echo -e "${{GREEN}}✅ Updated Dockerfile${{NC}}"
    fi
}}

# Update GitHub Actions
update_github_actions() {{
    if [ -d ".github/workflows" ]; then
        echo -e "\\n${{YELLOW}}🔄 Updating GitHub Actions...${{NC}}"
        
        for workflow in .github/workflows/*.yml .github/workflows/*.yaml; do
            if [ -f "$workflow" ]; then
                cp "$workflow" "${{workflow}}.backup"
                sed -i.bak "s/java-version:.*'{from_ver}'/java-version: '{to_ver}'/" "$workflow"
                sed -i.bak "s/java-version:.*\"{from_ver}\"/java-version: \"{to_ver}\"/" "$workflow"
                rm -f "${{workflow}}.bak"
                echo -e "${{GREEN}}✅ Updated $workflow${{NC}}"
            fi
        done
    fi
}}

# Test compilation
test_compilation() {{
    echo -e "\\n${{YELLOW}}🧪 Testing compilation...${{NC}}"
    
    if [ "$PROJECT_TYPE" = "maven" ]; then
        mvn clean compile
    elif [ "$PROJECT_TYPE" = "gradle" ]; then
        ./gradlew clean compileJava
    else
        echo -e "${{YELLOW}}⚠️  Manual compilation test required${{NC}}"
        return
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${{GREEN}}✅ Compilation successful!${{NC}}"
    else
        echo -e "${{RED}}❌ Compilation failed! Check errors above.${{NC}}"
        exit 1
    fi
}}

# Main execution
main() {{
    check_java_version
    create_backup
    detect_project_type
    
    case $PROJECT_TYPE in
        maven)
            update_maven
            ;;
        gradle)
            update_gradle
            ;;
        *)
            echo -e "${{YELLOW}}⚠️  Manual upgrade required${{NC}}"
            ;;
    esac
    
    update_dockerfile
    update_github_actions
    test_compilation
    
    echo -e "\\n${{GREEN}}╔════════════════════════════════════════╗${{NC}}"
    echo -e "${{GREEN}}║     Upgrade Completed Successfully     ║${{NC}}"
    echo -e "${{GREEN}}╚════════════════════════════════════════╝${{NC}}"
    echo ""
    echo -e "${{GREEN}}✅ Your project has been upgraded to Java {to_ver}${{NC}}"
    echo -e "\\n${{YELLOW}}Next steps:${{NC}}"
    echo "  1. Review changes with: git diff"
    echo "  2. Run tests: mvn test (or ./gradlew test)"
    echo "  3. Commit changes: git add . && git commit -m 'Upgrade to Java {to_ver}'"
    echo "  4. Push to remote: git push"
    echo ""
    echo -e "${{YELLOW}}Rollback if needed:${{NC}}"
    echo "  BACKUP_DIR=\\$(cat .java-upgrade-backup)"
    echo "  rm -rf ./*"
    echo "  cp -r \\$BACKUP_DIR/* ."
}}

# Run main function
main
""")
        os.chmod(script_path, 0o755)
        files.append(str(script_path))
        print(f"   ✅ Created: {script_path}")
        
        # 3. Maven POM example
        pom_path = workspace_path / f"pom.xml.java{to_ver}"
        with open(pom_path, "w") as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>java-{to_ver}-project</artifactId>
    <version>1.0.0-SNAPSHOT</version>

    <properties>
        <!-- Java {to_ver} -->
        <maven.compiler.source>{to_ver}</maven.compiler.source>
        <maven.compiler.target>{to_ver}</maven.compiler.target>
        <java.version>{to_ver}</java.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        
        <!-- Updated dependency versions for Java {to_ver} -->
        <spring-boot.version>3.2.3</spring-boot.version>
        <junit.version>5.10.2</junit.version>
    </properties>

    <dependencies>
        <!-- Spring Boot Starter (requires 3.0+ for Java 17+) -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
            <version>${{spring-boot.version}}</version>
        </dependency>

        <!-- JUnit 5 for testing -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${{junit.version}}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.12.1</version>
                <configuration>
                    <source>{to_ver}</source>
                    <target>{to_ver}</target>
                    <release>{to_ver}</release>
                </configuration>
            </plugin>

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.5</version>
            </plugin>
        </plugins>
    </build>
</project>
""")
        files.append(str(pom_path))
        print(f"   ✅ Created: {pom_path}")
        
        # 4. Gradle build.gradle example
        gradle_path = workspace_path / f"build.gradle.java{to_ver}"
        with open(gradle_path, "w") as f:
            f.write(f"""plugins {{
    id 'java'
    id 'application'
    id 'org.springframework.boot' version '3.2.3'
    id 'io.spring.dependency-management' version '1.1.4'
}}

group = 'com.example'
version = '1.0.0-SNAPSHOT'

java {{
    // Java {to_ver}
    sourceCompatibility = JavaVersion.VERSION_{to_ver}
    targetCompatibility = JavaVersion.VERSION_{to_ver}
    
    // Toolchain ensures correct Java version is used
    toolchain {{
        languageVersion = JavaLanguageVersion.of({to_ver})
        vendor = JvmVendorSpec.ADOPTIUM
    }}
}}

repositories {{
    mavenCentral()
}}

dependencies {{
    // Spring Boot
    implementation 'org.springframework.boot:spring-boot-starter'
    
    // Testing
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.2'
}}

tasks.withType(JavaCompile) {{
    options.encoding = 'UTF-8'
    options.compilerArgs += ['-parameters']
}}

tasks.named('test') {{
    useJUnitPlatform()
}}

application {{
    mainClass = 'com.example.Main'
}}
""")
        files.append(str(gradle_path))
        print(f"   ✅ Created: {gradle_path}")
        
        # 5. Dockerfile for Java {to_ver}
        dockerfile_path = workspace_path / f"Dockerfile.java{to_ver}"
        with open(dockerfile_path, "w") as f:
            f.write(f"""# Multi-stage build for Java {to_ver}
# Using Eclipse Temurin (recommended OpenJDK distribution)

# Build stage
FROM eclipse-temurin:{to_ver}-jdk-alpine AS build

WORKDIR /app

# Copy build files
COPY pom.xml .
COPY src ./src

# Build application (skip tests for faster build)
RUN ./mvnw clean package -DskipTests
# For Gradle: RUN ./gradlew build -x test

# Runtime stage (smaller image)
FROM eclipse-temurin:{to_ver}-jre-alpine

# Create non-root user for security
RUN addgroup -g 1001 appuser && \\
    adduser -u 1001 -G appuser -s /bin/sh -D appuser

WORKDIR /app

# Copy JAR from build stage
COPY --from=build /app/target/*.jar app.jar
# For Gradle: COPY --from=build /app/build/libs/*.jar app.jar

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# JVM options for Java {to_ver}
# ZGC is production-ready in Java 17+
ENV JAVA_OPTS="\\
    -Xms256m \\
    -Xmx512m \\
    -XX:+UseZGC \\
    -XX:+ZGenerational \\
    -XX:MaxRAMPercentage=75.0 \\
    -XX:InitialRAMPercentage=50.0 \\
    -XX:+ExitOnOutOfMemoryError \\
    -Djava.security.egd=file:/dev/./urandom"

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
""")
        files.append(str(dockerfile_path))
        print(f"   ✅ Created: {dockerfile_path}")
        
        # 6. CI/CD Configuration updates
        cicd_path = workspace_path / "CI_CD_UPDATES.md"
        with open(cicd_path, "w") as f:
            f.write(f"""# CI/CD Configuration Updates for Java {to_ver}

## GitHub Actions

Update `.github/workflows/build.yml`:
```yaml
name: Java CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up JDK {to_ver}
      uses: actions/setup-java@v4
      with:
        java-version: '{to_ver}'
        distribution: 'temurin'
        cache: 'maven'  # or 'gradle'
    
    - name: Build with Maven
      run: mvn clean install
    
    - name: Run tests
      run: mvn test
    
    - name: Build Docker image
      run: docker build -t myapp:java{to_ver} .
```

## GitLab CI

Update `.gitlab-ci.yml`:
```yaml
image: eclipse-temurin:{to_ver}-jdk

stages:
  - build
  - test
  - deploy

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"

cache:
  paths:
    - .m2/repository

build:
  stage: build
  script:
    - mvn clean compile
  artifacts:
    paths:
      - target/

test:
  stage: test
  script:
    - mvn test
  coverage: '/Total.*?([0-9]{{1,3}})%/'

docker:
  stage: deploy
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:java{to_ver} .
    - docker push $CI_REGISTRY_IMAGE:java{to_ver}
```

## Jenkins

Update `Jenkinsfile`:
```groovy
pipeline {{
    agent any
    
    tools {{
        jdk 'JDK-{to_ver}'
        maven 'Maven-3.9'
    }}
    
    stages {{
        stage('Build') {{
            steps {{
                sh 'mvn clean compile'
            }}
        }}
        
        stage('Test') {{
            steps {{
                sh 'mvn test'
            }}
            post {{
                always {{
                    junit 'target/surefire-reports/*.xml'
                }}
            }}
        }}
        
        stage('Package') {{
            steps {{
                sh 'mvn package -DskipTests'
            }}
        }}
        
        stage('Docker Build') {{
            steps {{
                sh 'docker build -t myapp:java{to_ver} .'
            }}
        }}
    }}
}}
```

## CircleCI

Update `.circleci/config.yml`:
```yaml
version: 2.1

orbs:
  java: circleci/openjdk@2.1

jobs:
  build:
    docker:
      - image: cimg/openjdk:{to_ver}.0
    
    steps:
      - checkout
      
      - restore_cache:
          keys:
            - v1-dependencies-{{{{ checksum "pom.xml" }}}}
      
      - run:
          name: Build
          command: mvn clean install -DskipTests
      
      - save_cache:
          paths:
            - ~/.m2
          key: v1-dependencies-{{{{ checksum "pom.xml" }}}}
      
      - run:
          name: Run tests
          command: mvn test
      
      - store_test_results:
          path: target/surefire-reports

workflows:
  version: 2
  build-and-test:
    jobs:
      - build
```

## Travis CI

Update `.travis.yml`:
```yaml
language: java
jdk:
  - openjdk{to_ver}

cache:
  directories:
    - $HOME/.m2

script:
  - mvn clean install
  - mvn test

after_success:
  - docker build -t myapp:java{to_ver} .
```

## Bitbucket Pipelines

Update `bitbucket-pipelines.yml`:
```yaml
image: eclipse-temurin:{to_ver}-jdk

pipelines:
  default:
    - step:
        name: Build and Test
        caches:
          - maven
        script:
          - mvn clean install
          - mvn test
        artifacts:
          - target/*.jar
    
    - step:
        name: Docker Build
        services:
          - docker
        script:
          - docker build -t myapp:java{to_ver} .
```

## Azure Pipelines

Update `azure-pipelines.yml`:
```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  jdkVersion: '{to_ver}'

steps:
- task: JavaToolInstaller@0
  inputs:
    versionSpec: '$(jdkVersion)'
    jdkArchitectureOption: 'x64'
    jdkSourceOption: 'PreInstalled'

- task: Maven@3
  inputs:
    mavenPomFile: 'pom.xml'
    goals: 'clean install'
    publishJUnitResults: true
    testResultsFiles: '**/surefire-reports/TEST-*.xml'
    javaHomeOption: 'JDKVersion'
    jdkVersionOption: '$(jdkVersion)'

- task: Docker@2
  inputs:
    command: 'build'
    Dockerfile: '**/Dockerfile'
    tags: 'java{to_ver}'
```

---
**Generated by AI DevOps Agent**
""")
        files.append(str(cicd_path))
        print(f"   ✅ Created: {cicd_path}")
        
        # 7. Quick Start README
        readme_path = workspace_path / "README.md"
        with open(readme_path, "w") as f:
            f.write(f"""# Java {from_ver} → {to_ver} Upgrade Package

## 📦 What's Included

This workspace contains everything you need to upgrade your Java project from **version {from_ver}** to **version {to_ver}**:

1. **JAVA_MIGRATION_GUIDE.md** - Comprehensive step-by-step migration guide
2. **upgrade_java.sh** - Automated upgrade script (recommended)
3. **pom.xml.java{to_ver}** - Example Maven configuration
4. **build.gradle.java{to_ver}** - Example Gradle configuration
5. **Dockerfile.java{to_ver}** - Docker configuration for Java {to_ver}
6. **CI_CD_UPDATES.md** - CI/CD pipeline configuration examples
7. **README.md** - This file

## 🚀 Quick Start

### Option 1: Automated Upgrade (Recommended)

```bash
# Make the script executable
chmod +x upgrade java.sh

# Run the upgrade
./upgrade_java.sh

# The script will:
# ✓ Check Java {to_ver} installation
# ✓ Create a backup of your project
# ✓ Detect project type (Maven/Gradle)
# ✓ Update all configuration files
# ✓ Update Dockerfile if present
# ✓ Update CI/CD configs
# ✓ Test compilation
```

### Option 2: Manual Migration

Follow the detailed steps in `JAVA_MIGRATION_GUIDE.md`

## 📋 Prerequisites

1. **Install Java {to_ver}**

   macOS:
   ```bash
   brew install openjdk@{to_ver}
   export JAVA_HOME=$(/usr/libexec/java_home -v {to_ver})
   ```

   Ubuntu/Debian:
   ```bash
   sudo apt update
   sudo apt install openjdk-{to_ver}-jdk
   export JAVA_HOME=/usr/lib/jvm/java-{to_ver}-openjdk-amd64
   ```

   Verify installation:
   ```bash
   java -version  # Should show: openjdk version "{to_ver}"
   ```

2. **Backup your project**
   ```bash
   cp -r . ../project-backup-$(date +%Y%m%d)
   ```

## 📝 Manual Configuration Changes

If you prefer manual updates:

### Maven (pom.xml)
```xml
<properties>
    <maven.compiler.source>{to_ver}</maven.compiler.source>
    <maven.compiler.target>{to_ver}</maven.compiler.target>
    <java.version>{to_ver}</java.version>
</properties>
```

### Gradle (build.gradle)
```groovy
java {{
    sourceCompatibility = JavaVersion.VERSION_{to_ver}
    targetCompatibility = JavaVersion.VERSION_{to_ver}
}}
```

### Dockerfile
```dockerfile
FROM eclipse-temurin:{to_ver}-jdk-alpine AS build
FROM eclipse-temurin:{to_ver}-jre-alpine
```

## ✅ Verification

After upgrade, verify everything works:

```bash
# 1. Clean build
mvn clean compile  # or ./gradlew clean build

# 2. Run tests
mvn test  # or ./gradlew test

# 3. Build Docker image (if applicable)
docker build -t myapp:java{to_ver} .

# 4. Run application 
mvn spring-boot:run  # or ./gradlew bootRun
```

## 🔄 Rollback

If something goes wrong:

```bash
# The automated script creates a backup
BACKUP_DIR=$(cat .java-upgrade-backup)
rm -rf ./*
cp -r $BACKUP_DIR/* .
```

Or manually restore from your backup.

## 📚 Additional Resources

- [Java {to_ver} Release Notes](https://openjdk.org/projects/jdk/{to_ver}/)
- [Migration Guide](https://docs.oracle.com/en/java/javase/{to_ver}/migrate/)
- [What's New in Java {to_ver}](https://openjdk.org/projects/jdk/{to_ver}/)

## ✅ Success Checklist

- [ ] Java {to_ver} installed and verified
- [ ] Project backup created
- [ ] Configuration files updated
- [ ] Project compiles successfully
- [ ] All tests pass
- [ ] Application runs correctly
- [ ] Docker image builds (if applicable)
- [ ] CI/CD pipelines updated
- [ ] Changes committed to Git

## 🆘 Support

If you encounter issues:
1. Check `JAVA_MIGRATION_GUIDE.md` for common problems
2. Review compilation errors: `mvn compile 2>&1 | tee errors.log`
3. Check Java compatibility of your dependencies

---

**Generated by AI DevOps Agent**  
**Date:** {datetime.now().strftime('%Y-%m-%d')}  
""")
        files.append(str(readme_path))
        print(f"   ✅ Created: {readme_path}")
        
        print(f"\n✅ Generated {len(files)} Java {from_ver}→{to_ver} upgrade files in {workspace_path}")
        return files

    def generate_jira_solution_files(self, task_info, workspace_path):
        """Generate files based on actual Jira ticket requirements"""
        files = []
        
        print(f"\n📋 Generating solution for Jira ticket {task_info.get('issue_key', 'N/A')}...")
        
        summary = task_info.get('summary', '')
        description = task_info.get('description', '')
        requirements = task_info.get('requirements', [])
        
        # 1. Solution Explanation
        explanation_path = workspace_path / "SOLUTION_EXPLANATION.md"
        with open(explanation_path, "w") as f:
            f.write(f"""# Solution for {task_info.get('issue_key', 'N/A')}

## Issue Summary
**Title:** {summary}
**Description:** {description[:500]}{'...' if len(description) > 500 else ''}

## Requirements Addressed
{chr(10).join(f'{i+1}. {req}' for i, req in enumerate(requirements))}

## Solution Implementation

{self._generate_solution_based_on_context(summary, description, requirements)}

---
**Generated by AI DevOps Agent**
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
        files.append(str(explanation_path))
        print(f"   ✅ Created: {explanation_path}")
        
        # 2. Generate context-specific implementation files
        if 'config' in summary.lower() or 'configuration' in description.lower():
            config_file = workspace_path / "centralized_config.py"
            with open(config_file, "w") as f:
                f.write(self._generate_config_management_code(summary, description, requirements))
            files.append(str(config_file))
            print(f"   ✅ Created: {config_file}")
        
        if 'report' in summary.lower() or 'reporting' in description.lower():
            # Create reporting format specification
            spec_file = workspace_path / "REPORTING_FORMAT_SPEC.md"
            with open(spec_file, "w") as f:
                f.write(self._generate_reporting_spec(summary, description, requirements))
            files.append(str(spec_file))
            print(f"   ✅ Created: {spec_file}")
            
            # Create automation script for unified reporting
            automation_file = workspace_path / "unified_reporter.py"
            with open(automation_file, "w") as f:
                f.write(self._generate_unified_reporter_code(summary, description, requirements))
            files.append(str(automation_file))
            print(f"   ✅ Created: {automation_file}")
            
            # Create example report template
            template_file = workspace_path / "report_template.json"
            with open(template_file, "w") as f:
                f.write(self._generate_report_template())
            files.append(str(template_file))
            print(f"   ✅ Created: {template_file}")
        
        # 3. README
        readme_path = workspace_path / "README.md"
        with open(readme_path, "w") as f:
            f.write(f"""# Solution for {task_info.get('issue_key', 'N/A')}

## Overview
**Jira Ticket:** [{task_info.get('issue_key', 'N/A')}]({self.jira_url}/browse/{ task_info.get('issue_key', 'N/A')})
**Summary:** {summary}

## Files
- `SOLUTION_EXPLANATION.md` - Detailed solution explanation
- Other implementation files as needed

## Usage
See SOLUTION_EXPLANATION.md for complete details.

---
**Generated by AI DevOps Agent**
""")
        files.append(str(readme_path))
        print(f"   ✅ Created: {readme_path}")
        
        print(f"\n✅ Generated {len(files)} solution files in {workspace_path}")
        return files

    def _generate_solution_based_on_context(self, summary, description, requirements):
        """Generate solution content based on actual ticket context"""
        # Analyze what the ticket is actually about
        full_text = f"{summary} {description}".lower()
        
        if 'solution' in full_text and 'report' in full_text:
            return """### Automated Solution Reporting System

**Problem:** Manual reporting processes are time-consuming and inconsistent.

**Solution:** Implement an automated reporting system that:
- Collects test results from multiple sources
- Generates reports in a unified format
- Automatically distributes reports to stakeholders
- Reduces manual effort significantly

**Implementation Steps:**
1. Create report template with standardized format
2. Implement data collection from test frameworks
3. Add report generation logic
4. Set up automated distribution (email/dashboard)
5. Test end-to-end workflow"""
        
        if 'centralized' in full_text and 'config' in full_text:
            return """### Centralized Configuration Management

**Problem:** Configuration scattered across multiple files and locations.

**Solution:** Implement a centralized configuration system that:
- Provides single source of truth for all configurations
- Supports environment-specific overrides
- Enables easy updates and maintenance
- Reduces configuration drift

**Implementation Steps:**
1. Audit existing configurations
2. Design centralized configuration structure
3. Create configuration management service
4. Migrate existing configs to centralized system
5. Update all consumers to use new system"""
        
        # Generic solution if no specific pattern matches
        return f"""### Implementation Approach

Based on the requirements analysis, this solution addresses:
{chr(10).join(f'- {req}' for req in requirements)}

**Key Components:**
1. Core implementation files
2. Configuration management
3. Documentation and examples
4. Testing framework

**Deployment Steps:**
1. Review the generated code
2. Customize for your environment
3. Run tests to verify functionality
4. Deploy to target environment
5. Monitor and validate"""

    def _generate_reporting_spec(self, summary, description, requirements):
        """Generate comprehensive reporting format specification"""
        return f"""# Unified Reporting Format Specification

## Overview
This document defines the standard format for all solution test reports to ensure consistency, ease of parsing, and integration across different testing frameworks and environments.

**Version:** 1.0  
**Status:** Draft  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}

## Objectives
1. Standardize report format across all test solutions
2. Enable automated parsing and aggregation
3. Support multiple output formats (JSON, XML, HTML)
4. Facilitate integration with CI/CD pipelines
5. Provide clear audit trail and traceability

---

## Report Structure

### 1. Metadata Section
Every report MUST include the following metadata:

```json
{{
  "metadata": {{
    "report_id": "UUID",
    "report_version": "1.0",
    "generated_at": "ISO-8601 timestamp",
    "generator": {{
      "name": "Test framework name",
      "version": "Framework version"
    }},
    "environment": {{
      "name": "dev|staging|prod",
      "host": "hostname",
      "os": "Operating system"
    }},
    "test_suite": {{
      "name": "Test suite name",
      "version": "Test version",
      "tags": ["tag1", "tag2"]
    }}
  }}
}}
```

**Field Descriptions:**
- `report_id`: Unique UUID for this report instance
- `generated_at`: ISO-8601 timestamp (e.g., "2026-03-05T10:30:00Z")
- `environment.name`: Target environment where tests ran
- `test_suite.tags`: Categorization tags (e.g., ["smoke", "regression"])

---

### 2. Execution Summary
High-level summary of test execution:

```json
{{
  "summary": {{
    "total_tests": 150,
    "passed": 145,
    "failed": 3,
    "skipped": 2,
    "errors": 0,
    "duration_ms": 45000,
    "start_time": "ISO-8601 timestamp",
    "end_time": "ISO-8601 timestamp",
    "success_rate": 96.67,
    "status": "PASSED|FAILED|ERROR"
  }}
}}
```

**Calculation Rules:**
- `success_rate` = (passed / total_tests) × 100
- `status` = "PASSED" if failed == 0 and errors == 0, else "FAILED"
- `duration_ms` = Total execution time in milliseconds

---

### 3. Test Results
Detailed results for each test case:

```json
{{
  "test_results": [
    {{
      "test_id": "test_login_valid_credentials",
      "test_name": "Verify login with valid credentials",
      "description": "Tests successful login flow",
      "status": "PASSED|FAILED|SKIPPED|ERROR",
      "duration_ms": 1250,
      "start_time": "ISO-8601 timestamp",
      "end_time": "ISO-8601 timestamp",
      "assertions": {{
        "total": 5,
        "passed": 5,
        "failed": 0
      }},
      "tags": ["authentication", "smoke"],
      "category": "functional",
      "severity": "critical|high|medium|low",
      "failure_details": {{
        "message": "Error message if failed",
        "stack_trace": "Full stack trace",
        "screenshot": "path/to/screenshot.png",
        "logs": "Relevant log excerpts"
      }},
      "retry_count": 0,
      "flaky": false
    }}
  ]
}}
```

**Status Values:**
- `PASSED`: Test completed successfully
- `FAILED`: Test failed with assertion error
- `SKIPPED`: Test was intentionally skipped
- `ERROR`: Test encountered an error (not assertion failure)

**Severity Levels:**
- `critical`: Must pass for release
- `high`: Important functionality
- `medium`: Standard functionality
- `low`: Nice-to-have features

---

### 4. Coverage Information
Code coverage metrics (if applicable):

```json
{{
  "coverage": {{
    "line_coverage": 85.5,
    "branch_coverage": 78.3,
    "function_coverage": 92.1,
    "statement_coverage": 84.7,
    "covered_lines": 8550,
    "total_lines": 10000,
    "report_path": "coverage/index.html"
  }}
}}
```

---

### 5. Performance Metrics
Performance-related measurements:

```json
{{
  "performance": {{
    "average_response_time_ms": 250,
    "max_response_time_ms": 1500,
    "min_response_time_ms": 50,
    "p95_response_time_ms": 800,
    "p99_response_time_ms": 1200,
    "throughput_requests_per_sec": 100,
    "error_rate_percent": 0.5
  }}
}}
```

---

### 6. Artifacts
Links to generated artifacts:

```json
{{
  "artifacts": {{
    "screenshots": ["url1", "url2"],
    "videos": ["url1"],
    "logs": ["url1", "url2"],
    "reports": {{
      "html": "path/to/report.html",
      "json": "path/to/report.json",
      "xml": "path/to/report.xml"
    }}
  }}
}}
```

---

### 7. Integration Data
CI/CD and version control information:

```json
{{
  "integration": {{
    "ci_system": "Jenkins|GitLab|GitHub Actions",
    "build_id": "12345",
    "build_url": "https://ci.example.com/build/12345",
    "commit": {{
      "sha": "abc123def456",
      "branch": "main",
      "author": "john.doe@example.com",
      "message": "Fix login bug",
      "timestamp": "ISO-8601 timestamp"
    }},
    "pull_request": {{
      "number": 123,
      "url": "https://github.com/org/repo/pull/123"
    }}
  }}
}}
```

---

## Complete Example Report

```json
{{
  "metadata": {{
    "report_id": "550e8400-e29b-41d4-a716-446655440000",
    "report_version": "1.0",
    "generated_at": "2026-03-05T10:30:00Z",
    "generator": {{
      "name": "PyTest",
      "version": "7.4.0"
    }},
    "environment": {{
      "name": "staging",
      "host": "test-runner-01",
      "os": "Ubuntu 22.04"
    }},
    "test_suite": {{
      "name": "Vertex Solution Tests",
      "version": "2.0.0",
      "tags": ["regression", "api"]
    }}
  }},
  "summary": {{
    "total_tests": 150,
    "passed": 145,
    "failed": 3,
    "skipped": 2,
    "errors": 0,
    "duration_ms": 45000,
    "start_time": "2026-03-05T10:30:00Z",
    "end_time": "2026-03-05T10:30:45Z",
    "success_rate": 96.67,
    "status": "FAILED"
  }},
  "test_results": [
    {{
      "test_id": "test_login_valid",
      "test_name": "Verify login with valid credentials",
      "description": "Tests successful login flow with valid user credentials",
      "status": "PASSED",
      "duration_ms": 1250,
      "start_time": "2026-03-05T10:30:00Z",
      "end_time": "2026-03-05T10:30:01.250Z",
      "assertions": {{
        "total": 5,
        "passed": 5,
        "failed": 0
      }},
      "tags": ["authentication", "smoke"],
      "category": "functional",
      "severity": "critical",
      "retry_count": 0,
      "flaky": false
    }}
  ],
  "coverage": {{
    "line_coverage": 85.5,
    "branch_coverage": 78.3,
    "function_coverage": 92.1,
    "covered_lines": 8550,
    "total_lines": 10000,
    "report_path": "coverage/index.html"
  }},
  "performance": {{
    "average_response_time_ms": 250,
    "p95_response_time_ms": 800,
    "p99_response_time_ms": 1200
  }},
  "artifacts": {{
    "reports": {{
      "html": "reports/test-report.html",
      "json": "reports/test-report.json"
    }}
  }},
  "integration": {{
    "ci_system": "GitLab CI",
    "build_id": "12345",
    "build_url": "https://gitlab.com/vertex/project/-/jobs/12345",
    "commit": {{
      "sha": "abc123def456",
      "branch": "main",
      "author": "developer@vertex.com",
      "message": "Add new test cases",
      "timestamp": "2026-03-05T09:00:00Z"
    }}
  }}
}}
```

---

## Field Mapping Guide

### From JUnit XML to Unified Format
| JUnit XML | Unified Format |
|-----------|----------------|
| `testsuites/@tests` | `summary.total_tests` |
| `testsuites/@failures` | `summary.failed` |
| `testsuites/@time` | `summary.duration_ms` (convert to ms) |
| `testcase/@name` | `test_results[].test_name` |
| `testcase/@time` | `test_results[].duration_ms` |
| `testcase/failure` | `test_results[].status = "FAILED"` |

### From PyTest JSON to Unified Format
| PyTest JSON | Unified Format |
|-------------|----------------|
| `summary.total` | `summary.total_tests` |
| `summary.passed` | `summary.passed` |
| `summary.failed` | `summary.failed` |
| `tests[].nodeid` | `test_results[].test_id` |
| `tests[].outcome` | `test_results[].status` (map values) |
| `tests[].duration` | `test_results[].duration_ms` (convert to ms) |

---

## Data Types

| Field | Type | Format | Required |
|-------|------|--------|----------|
| `report_id` | String | UUID v4 | Yes |
| `generated_at` | String | ISO-8601 | Yes |
| `total_tests` | Integer | >= 0 | Yes |
| `duration_ms` | Integer | >= 0 | Yes |
| `success_rate` | Float | 0-100 with 2 decimals | Yes |
| `status` | Enum | PASSED\\|FAILED\\|ERROR | Yes |
| `tags` | Array | String[] | No |
| `severity` | Enum | critical\\|high\\|medium\\|low | No |

---

## Validation Rules

1. **Required Fields**: All fields marked "Required: Yes" must be present
2. **Status Logic**: If any test has status "FAILED", summary.status must be "FAILED"
3. **Time Consistency**: `end_time` must be >= `start_time`
4. **Count Consistency**: `total_tests` = `passed` + `failed` + `skipped` + `errors`
5. **Success Rate**: Must match calculated value within 0.01%
6. **UUID Format**: All IDs must be valid UUID v4 format

---

## Output Formats

### JSON (Primary)
- Default and recommended format
- File extension: `.json`
- MIME type: `application/json`
- UTF-8 encoding

### XML (Legacy Support)
- For compatibility with older systems
- File extension: `.xml`
- Root element: `<test_report>`

### HTML (Human-Readable)
- For viewing in browsers
- File extension: `.html`
- Must include CSS for styling

---

## Implementation Checklist

- [ ] Report generator validates all required fields
- [ ] Timestamps use ISO-8601 format with timezone
- [ ] File names include timestamp: `test-report-20260305-103000.json`
- [ ] Reports stored in designated directory structure
- [ ] Validation against JSON schema before publishing
- [ ] Automated tests for report generation
- [ ] Documentation for consumers
- [ ] CI/CD integration examples

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-05 | Initial specification |

---

**Generated by AI DevOps Agent**  
**For Jira Ticket:** STBBS-650  
**Status:** Ready for Review
"""

    def _generate_unified_reporter_code(self, summary, description, requirements):
        """Generate Python code for unified reporting"""
        return '''#!/usr/bin/env python3
"""
Unified Test Reporter
Converts various test formats to the unified reporting format

Usage:
    python unified_reporter.py --input test-results.xml --format junit --output report.json
    python unified_reporter.py --input pytest-results.json --format pytest --output report.json
"""

import json
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse


class UnifiedReporter:
    """Converts test results to unified reporting format"""
    
    REPORT_VERSION = "1.0"
    
    def __init__(self, environment: str = "dev", test_suite_name: str = "Test Suite"):
        self.environment = environment
        self.test_suite_name = test_suite_name
    
    def create_report_template(self) -> Dict[str, Any]:
        """Create base report structure"""
        return {
            "metadata": {
                "report_id": str(uuid.uuid4()),
                "report_version": self.REPORT_VERSION,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generator": {
                    "name": "UnifiedReporter",
                    "version": "1.0.0"
                },
                "environment": {
                    "name": self.environment,
                    "host": Path.cwd().as_posix(),
                    "os": "Python"
                },
                "test_suite": {
                    "name": self.test_suite_name,
                    "version": "1.0.0",
                    "tags": []
                }
            },
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
                "duration_ms": 0,
                "start_time": "",
                "end_time": "",
                "success_rate": 0.0,
                "status": "PASSED"
            },
            "test_results": [],
            "artifacts": {
                "reports": {}
            }
        }
    
    def convert_junit_xml(self, xml_path: Path) -> Dict[str, Any]:
        """Convert JUnit XML format to unified format"""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        report = self.create_report_template()
        
        # Parse summary from testsuites element
        if root.tag == "testsuites":
            report["summary"]["total_tests"] = int(root.get("tests", 0))
            report["summary"]["failed"] = int(root.get("failures", 0))
            report["summary"]["errors"] = int(root.get("errors", 0))
            report["summary"]["skipped"] = int(root.get("skipped", 0))
            report["summary"]["duration_ms"] = int(float(root.get("time", 0)) * 1000)
            
            testsuites = root.findall("testsuite")
        else:
            testsuites = [root]
        
        # Parse individual test cases
        for testsuite in testsuites:
            for testcase in testsuite.findall("testcase"):
                test_result = {
                    "test_id": f"{testcase.get(\\'classname\\', \\'unknown\\')}.{testcase.get(\\'name\\', \\'unknown\\')}",
                    "test_name": testcase.get("name", "Unknown Test"),
                    "description": "",
                    "status": "PASSED",
                    "duration_ms": int(float(testcase.get("time", 0)) * 1000),
                    "start_time": report["metadata"]["generated_at"],
                    "end_time": report["metadata"]["generated_at"],
                    "assertions": {
                        "total": 1,
                        "passed": 1,
                        "failed": 0
                    },
                    "tags": [],
                    "category": "functional",
                    "severity": "medium",
                    "retry_count": 0,
                    "flaky": False
                }
                
                # Check for failures
                failure = testcase.find("failure")
                if failure is not None:
                    test_result["status"] = "FAILED"
                    test_result["failure_details"] = {
                        "message": failure.get("message", ""),
                        "stack_trace": failure.text or "",
                        "screenshot": "",
                        "logs": ""
                    }
                    test_result["assertions"]["failed"] = 1
                    test_result["assertions"]["passed"] = 0
                
                # Check for errors
                error = testcase.find("error")
                if error is not None:
                    test_result["status"] = "ERROR"
                    test_result["failure_details"] = {
                        "message": error.get("message", ""),
                        "stack_trace": error.text or "",
                        "screenshot": "",
                        "logs": ""
                    }
                
                # Check for skipped
                skipped = testcase.find("skipped")
                if skipped is not None:
                    test_result["status"] = "SKIPPED"
                
                report["test_results"].append(test_result)
        
        # Calculate passed tests
        report["summary"]["passed"] = report["summary"]["total_tests"] - \\
                                      report["summary"]["failed"] - \\
                                      report["summary"]["errors"] - \\
                                      report["summary"]["skipped"]
        
        # Calculate success rate
        if report["summary"]["total_tests"] > 0:
            report["summary"]["success_rate"] = round(
                (report["summary"]["passed"] / report["summary"]["total_tests"]) * 100, 2
            )
        
        # Determine overall status
        if report["summary"]["failed"] > 0 or report["summary"]["errors"] > 0:
            report["summary"]["status"] = "FAILED"
        
        return report
    
    def convert_pytest_json(self, json_path: Path) -> Dict[str, Any]:
        """Convert PyTest JSON format to unified format"""
        with open(json_path, "r") as f:
            pytest_data = json.load(f)
        
        report = self.create_report_template()
        
        # Parse summary
        if "summary" in pytest_data:
            summary = pytest_data["summary"]
            report["summary"]["total_tests"] = summary.get("total", 0)
            report["summary"]["passed"] = summary.get("passed", 0)
            report["summary"]["failed"] = summary.get("failed", 0)
            report["summary"]["skipped"] = summary.get("skipped", 0)
            report["summary"]["errors"] = summary.get("error", 0)
        
        # Parse test results
        for test in pytest_data.get("tests", []):
            outcome = test.get("outcome", "passed")
            status_map = {
                "passed": "PASSED",
                "failed": "FAILED",
                "skipped": "SKIPPED",
                "error": "ERROR"
            }
            
            test_result = {
                "test_id": test.get("nodeid", "unknown"),
                "test_name": test.get("name", "Unknown Test"),
                "description": test.get("doc", ""),
                "status": status_map.get(outcome, "UNKNOWN"),
                "duration_ms": int(test.get("duration", 0) * 1000),
                "start_time": report["metadata"]["generated_at"],
                "end_time": report["metadata"]["generated_at"],
                "assertions": {
                    "total": 1,
                    "passed": 1 if outcome == "passed" else 0,
                    "failed": 1 if outcome == "failed" else 0
                },
                "tags": test.get("markers", []),
                "category": "functional",
                "severity": "medium",
                "retry_count": 0,
                "flaky": False
            }
            
            if outcome == "failed":
                call = test.get("call", {})
                test_result["failure_details"] = {
                    "message": call.get("longrepr", ""),
                    "stack_trace": "",
                    "screenshot": "",
                    "logs": ""
                }
            
            report["test_results"].append(test_result)
        
        # Calculate success rate
        if report["summary"]["total_tests"] > 0:
            report["summary"]["success_rate"] = round(
                (report["summary"]["passed"] / report["summary"]["total_tests"]) * 100, 2
            )
        
        # Determine overall status
        if report["summary"]["failed"] > 0 or report["summary"]["errors"] > 0:
            report["summary"]["status"] = "FAILED"
        
        return report
    
    def validate_report(self, report: Dict[str, Any]) -> List[str]:
        """Validate report against specification"""
        errors = []
        
        # Check required fields
        if "metadata" not in report:
            errors.append("Missing required field: metadata")
        if "summary" not in report:
            errors.append("Missing required field: summary")
        if "test_results" not in report:
            errors.append("Missing required field: test_results")
        
        # Validate counts
        summary = report.get("summary", {})
        total = summary.get("total_tests", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)
        errors_count = summary.get("errors", 0)
        
        if passed + failed + skipped + errors_count != total:
            errors.append(f"Test count mismatch: {passed}+{failed}+{skipped}+{errors_count} != {total}")
        
        # Validate success rate
        if total > 0:
            expected_rate = round((passed / total) * 100, 2)
            actual_rate = summary.get("success_rate", 0)
            if abs(expected_rate - actual_rate) > 0.01:
                errors.append(f"Success rate mismatch: expected {expected_rate}, got {actual_rate}")
        
        return errors
    
    def save_report(self, report: Dict[str, Any], output_path: Path, format: str = "json"):
        """Save report in specified format"""
        if format == "json":
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
            print(f"✅ Report saved: {output_path}")
        else:
            print(f"⚠️  Format {format} not yet implemented")


def main():
    parser = argparse.ArgumentParser(description="Convert test results to unified format")
    parser.add_argument("--input", required=True, help="Input test results file")
    parser.add_argument("--format", required=True, choices=["junit", "pytest"], 
                       help="Input format")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--environment", default="dev", help="Test environment")
    parser.add_argument("--suite-name", default="Test Suite", help="Test suite name")
    
    args = parser.parse_args()
    
    reporter = UnifiedReporter(
        environment=args.environment,
        test_suite_name=args.suite_name
    )
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return 1
    
    print(f"🔄 Converting {args.format} format to unified format...")
    
    if args.format == "junit":
        report = reporter.convert_junit_xml(input_path)
    elif args.format == "pytest":
        report = reporter.convert_pytest_json(input_path)
    else:
        print(f"❌ Unsupported format: {args.format}")
        return 1
    
    print(f"✅ Converted {report[\\'summary\\'][\\'total_tests\\']} tests")
    
    # Validate report
    print("🔍 Validating report...")
    errors = reporter.validate_report(report)
    if errors:
        print("⚠️  Validation warnings:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Report validated successfully")
    
    # Save report
    output_path = Path(args.output)
    reporter.save_report(report, output_path)
    
    print(f"\\n📊 Summary:")
    print(f"   Total: {report[\\'summary\\'][\\'total_tests\\']}")
    print(f"   Passed: {report[\\'summary\\'][\\'passed\\']}")
    print(f"   Failed: {report[\\'summary\\'][\\'failed\\']}")
    print(f"   Success Rate: {report[\\'summary\\'][\\'success_rate\\']}%")
    print(f"   Status: {report[\\'summary\\'][\\'status\\']}")
    
    return 0


if __name__ == "__main__":
    exit(main())
'''

    def _generate_report_template(self):
        """Generate example report template"""
        return '''{
  "metadata": {
    "report_id": "GENERATE_UUID_HERE",
    "report_version": "1.0",
    "generated_at": "ISO_8601_TIMESTAMP",
    "generator": {
      "name": "YourTestFramework",
      "version": "1.0.0"
    },
    "environment": {
      "name": "dev|staging|prod",
      "host": "hostname",
      "os": "Operating System"
    },
    "test_suite": {
      "name": "Your Test Suite Name",
      "version": "1.0.0",
      "tags": ["smoke", "regression"]
    }
  },
  "summary": {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": 0,
    "duration_ms": 0,
    "start_time": "ISO_8601_TIMESTAMP",
    "end_time": "ISO_8601_TIMESTAMP",
    "success_rate": 0.0,
    "status": "PASSED|FAILED|ERROR"
  },
  "test_results": [
    {
      "test_id": "unique_test_identifier",
      "test_name": "Human readable test name",
      "description": "What this test verifies",
      "status": "PASSED",
      "duration_ms": 1250,
      "start_time": "ISO_8601_TIMESTAMP",
      "end_time": "ISO_8601_TIMESTAMP",
      "assertions": {
        "total": 5,
        "passed": 5,
        "failed": 0
      },
      "tags": ["authentication", "smoke"],
      "category": "functional",
      "severity": "critical",
      "failure_details": {
        "message": "Error message if test failed",
        "stack_trace": "Full stack trace",
        "screenshot": "path/to/screenshot.png",
        "logs": "Relevant log excerpts"
      },
      "retry_count": 0,
      "flaky": false
    }
  ],
  "coverage": {
    "line_coverage": 85.5,
    "branch_coverage": 78.3,
    "function_coverage": 92.1,
    "covered_lines": 8550,
    "total_lines": 10000,
    "report_path": "coverage/index.html"
  },
  "performance": {
    "average_response_time_ms": 250,
    "max_response_time_ms": 1500,
    "min_response_time_ms": 50,
    "p95_response_time_ms": 800,
    "p99_response_time_ms": 1200
  },
  "artifacts": {
    "screenshots": [],
    "videos": [],
    "logs": [],
    "reports": {
      "html": "path/to/report.html",
      "json": "path/to/report.json",
      "xml": "path/to/report.xml"
    }
  },
  "integration": {
    "ci_system": "Jenkins|GitLab|GitHub Actions",
    "build_id": "12345",
    "build_url": "https://ci.example.com/build/12345",
    "commit": {
      "sha": "abc123def456",
      "branch": "main",
      "author": "developer@example.com",
      "message": "Commit message",
      "timestamp": "ISO_8601_TIMESTAMP"
    }
  }
}
'''

    def _generate_config_management_code(self, summary, description, requirements):
        """Generate centralized configuration management code"""
        return '''#!/usr/bin/env python3
"""
Centralized Configuration Management System
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigurationManager:
    """Centralized configuration manager"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.configs = {}
        self.load_all_configs()
    
    def load_all_configs(self):
        """Load all configuration files"""
        config_files = self.config_dir.glob("*.json")
        for config_file in config_files:
            config_name = config_file.stem
            with open(config_file, \\'r\\') as f:
                self.configs[config_name] = json.load(f)
        print(f"Loaded {len(self.configs)} configuration(s)")
    
    def get_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve configuration by name"""
        return self.configs.get(config_name)
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]):
        """Save configuration to file"""
        config_path = self.config_dir / f"{config_name}.json"
        with open(config_path, \\'w\\') as f:
            json.dump(config_data, f, indent=2)
        self.configs[config_name] = config_data
        print(f"Saved configuration: {config_name}")
'''

    def generate_sonarqube_upgrade_files(self, task_info, workspace_path):
        """Generate SonarQube specific upgrade files"""
        files = []
        version = task_info['version']
        print(f"\n⬆️  Generating SonarQube {version} upgrade files...")
        
        # Implementation for SonarQube upgrade...
        # (Similar structure to Java upgrade but SonarQube-specific)
        
        return files

    def generate_python_upgrade_files(self, task_info, workspace_path):
        """Generate Python upgrade files"""
        files = []
        from_ver = task_info['from_version']
        to_ver = task_info['to_version']
        print(f"\n⬆️  Generating Python {from_ver}→{to_ver} upgrade files...")
        
        # Implementation for Python upgrade...
        
        return files

    def generate_node_upgrade_files(self, task_info, workspace_path):
        """Generate Node.js upgrade files"""
        files = []
        from_ver = task_info['from_version']
        to_ver = task_info['to_version']
        print(f"\n⬆️  Generating Node.js {from_ver}→{to_ver} upgrade files...")
        
        # Implementation for Node.js upgrade...
        
        return files

    def commit_and_push(self, branch_name, files, task_info):
        """Commit and push generated files"""
        if not files:
            print("⚠️  No files to commit")
            return False
        
        print(f"\n📦 Adding {len(files)} files to Git...")
        try:
            for file in files:
                subprocess.run(["git", "add", file], check=True)
                print(f"   ✅ Added: {file}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to add files: {e}")
            return False
        
        # Create meaningful commit message
        if task_info["type"] == "jira":
            commit_msg = f"feat: Implement solution for {task_info.get('issue_key', 'N/A')}"
        elif task_info["type"] == "java_upgrade":
            commit_msg = f"chore: Upgrade Java from {task_info['from_version']} to {task_info['to_version']}"
        else:
            commit_msg = f"feat: {task_info.get('software', 'Software')} upgrade automation"
        
        print(f"\n💾 Committing with message: {commit_msg}")
        try:
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            print("   ✅ Committed successfully")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to commit: {e}")
            return False
        
        print(f"\n📤 Pushing branch {branch_name} to remote...")
        try:
            subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
            print(f"   ✅ Pushed to remote")
            print(f"\n🔗 Create PR: https://github.com/{self.git_owner}/{self.git_repo}/pull/new/{branch_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Failed to push: {e}")
            return False

    def run_workflow(self, prompt):
        """Main workflow execution"""
        print("\n" + "="*70)
        print("🤖 AI DEVOPS AGENT - INTELLIGENT WORKFLOW")
        print("="*70 + "\n")
        
        # Analyze the prompt to understand the task
        task_info = self.analyze_prompt(prompt)
        
        if task_info["type"] == "unknown":
            print(f"❌ Could not determine action from prompt: {prompt}")
            print("\n💡 Supported tasks:")
            print("   - Upgrade Java from X to Y")
            print("   - Upgrade Python from X to Y")
            print("   - Upgrade Node.js from X to Y")
            print("   - Upgrade SonarQube to version X")
            print("   - jira: ISSUE-KEY")
            return
        
        # If Jira ticket, fetch details first
        if task_info["type"] == "jira":
            issue_data = self.get_jira_issue(task_info["issue_key"])
            if issue_data:
                jira_context = self.explain_jira_issue(issue_data)
                task_info.update(jira_context)
                
                response = input("\n👉 Proceed with automated Workflow? (yes/no): ").strip().lower()
                if response not in ['yes', 'y']:
                    print("\n⛔ Workflow cancelled.")
                    return
            else:
                print("\n⚠️  Could not fetch Jira details.")
                return
        
        print("\n🔄 Starting intelligent workflow...\n")
        
        # Create branch specific to this task
        branch_name = self.create_branch(task_info)
        if not branch_name:
            print("❌ Failed to create branch")
            return
        
        # Create task-specific workspace
        workspace_path = self.create_workspace_for_task(task_info, branch_name)
        
        # Generate files based on the ACTUAL task
        files = self.generate_files_for_task(task_info, workspace_path)
        
        # Commit and push
        if files:
            self.commit_and_push(branch_name, files, task_info)
        
        print("\n" + "="*70)
        print("✅ WORKFLOW COMPLETE")
        print("="*70 + "\n")
        print(f"📁 Workspace: {workspace_path}")
        print(f"🌿 Branch: {branch_name}")
        print(f"📝 Files: {len(files)}")
        print(f"\n🔗 Next: Review files and create PR on GitHub")


if __name__ == "__main__":
    agent = AIDevOpsAgent()
    if len(sys.argv) > 1:
        user_prompt = sys.argv[1]
    else:
        user_prompt = input("Enter your prompt or Jira link: ")
    agent.run_workflow(user_prompt)
