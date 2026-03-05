# Java 11 to 21 Upgrade - Complete Guide

## ✅ What Has Been Created

Your AI DevOps Agent has generated a complete Java upgrade automation package in the `feature/upgrade-AI-Devops-Agent` branch:

### 📁 Files Created

1. **java_upgrade_guide.md** - Comprehensive migration guide covering:
   - Step-by-step upgrade instructions
   - Maven and Gradle configuration changes
   - Docker and CI/CD updates
   - Common migration issues and solutions
   - Testing and validation checklist

2. **java_upgrade.sh** - Automated upgrade script featuring:
   - Automatic project type detection (Maven/Gradle)
   - Backup creation before any changes
   - Automatic configuration file updates
   - Java version verification
   - Rollback support

3. **pom.xml.example** - Maven configuration reference with:
   - Java 21 compiler settings
   - Updated plugin versions
   - Modern dependency versions
   - Best practices for Java 21

4. **build.gradle.example** - Gradle configuration reference with:
   - Java 21 toolchain configuration
   - Updated plugin versions
   - Modern dependency management

5. **Dockerfile.example** - Docker configuration with:
   - Multi-stage build for Java 21
   - Eclipse Temurin JDK/JRE 21
   - Security best practices
   - Health checks and JVM optimization

## 🚀 Quick Start - Automated Upgrade

### Option 1: Using the Automated Script (Recommended)

```bash
# Clone or navigate to your Java project
cd /path/to/your/java/project

# Download the upgrade script from the feature branch
curl -O https://raw.githubusercontent.com/Tejakrishna-b/AI-Devops-Agent/feature/upgrade-AI-Devops-Agent/workspace/java_upgrade.sh

# Make it executable
chmod +x java_upgrade.sh

# Run the upgrade
./java_upgrade.sh

# The script will:
# ✓ Create a backup (java_11_backup_TIMESTAMP)
# ✓ Detect your project type (Maven/Gradle)
# ✓ Update configuration files
# ✓ Update Dockerfile if present
# ✓ Update CI/CD configs
# ✓ Verify Java 21 is installed

# If something goes wrong, rollback:
./java_upgrade.sh rollback
```

### Option 2: Manual Step-by-Step Migration

```bash
# 1. Reference the comprehensive guide
curl -O https://raw.githubusercontent.com/Tejakrishna-b/AI-Devops-Agent/feature/upgrade-AI-Devops-Agent/workspace/java_upgrade_guide.md

# 2. Read through the guide
cat java_upgrade_guide.md

# 3. Download example configurations
curl -O https://raw.githubusercontent.com/Tejakrishna-b/AI-Devops-Agent/feature/upgrade-AI-Devops-Agent/workspace/pom.xml.example
curl -O https://raw.githubusercontent.com/Tejakrishna-b/AI-Devops-Agent/feature/upgrade-AI-Devops-Agent/workspace/build.gradle.example
curl -O https://raw.githubusercontent.com/Tejakrishna-b/AI-Devops-Agent/feature/upgrade-AI-Devops-Agent/workspace/Dockerfile.example

# 4. Manually update your project files based on the examples
```

## 📋 Pre-Upgrade Checklist

Before running the upgrade, ensure:

- ✅ **Java 21 is installed** on your system
  ```bash
  # Check Java version
  java -version
  
  # Install Java 21 (macOS with Homebrew)
  brew install openjdk@21
  
  # Set JAVA_HOME
  export JAVA_HOME=$(/usr/libexec/java_home -v 21)
  ```

- ✅ **Your project builds successfully** with Java 11
  ```bash
  # For Maven
  mvn clean install
  
  # For Gradle
  ./gradlew build
  ```

- ✅ **All changes are committed** to version control
  ```bash
  git status
  git add .
  git commit -m "Pre-Java 21 upgrade checkpoint"
  ```

- ✅ **Dependencies are compatible** with Java 21
  - Spring Boot: Use version 3.0+
  - JUnit: Use version 5.x
  - Check your library versions

## 🔧 Post-Upgrade Steps

After running the automated script or manual upgrade:

### 1. Verify Configuration Changes

```bash
# Check Maven configuration
grep -A 3 "<maven.compiler" pom.xml

# Check Gradle configuration
grep "sourceCompatibility" build.gradle

# Check Dockerfile
grep "FROM eclipse-temurin:21" Dockerfile
```

### 2. Clean and Rebuild

```bash
# For Maven
mvn clean compile

# For Gradle
./gradlew clean build
```

### 3. Run Tests

```bash
# For Maven
mvn test

# For Gradle
./gradlew test
```

### 4. Update Your IDE

**IntelliJ IDEA:**
1. File → Project Structure → Project SDK → Add SDK → Java 21
2. File → Project Structure → Project Language Level → 21
3. File → Settings → Build, Execution, Deployment → Compiler → Java Compiler → Target bytecode version: 21

**VS Code:**
1. Install Java Extension Pack
2. Update settings.json:
```json
{
  "java.configuration.runtimes": [
    {
      "name": "JavaSE-21",
      "path": "/path/to/jdk-21",
      "default": true
    }
  ]
}
```

**Eclipse:**
1. Window → Preferences → Java → Installed JREs → Add JDK 21
2. Project → Properties → Java Compiler → Compiler compliance level: 21

### 5. Docker Build and Test

```bash
# Build Docker image
docker build -t my-java-app:java21 .

# Run container
docker run -p 8080:8080 my-java-app:java21

# Test the application
curl http://localhost:8080/actuator/health
```

## 🎯 Common Issues and Solutions

### Issue: "java: invalid source release: 21"

**Solution:** Maven compiler plugin version is too old
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.12.0</version> <!-- Minimum 3.11.0 -->
</plugin>
```

### Issue: Deprecated API warnings

**Solution:** Review and update deprecated code
```bash
# Find deprecated API usage
mvn compile | grep deprecated

# Common replacements in Java 21:
# - SecurityManager → removed (use alternatives)
# - Thread.stop() → use interruption
# - Applet API → removed
```

### Issue: Docker build fails

**Solution:** Clear Docker cache and rebuild
```bash
docker system prune -a
docker build --no-cache -t my-java-app:java21 .
```

## 📊 Validation Checklist

- [ ] Java 21 is installed and active (`java -version`)
- [ ] Project compiles without errors
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Docker image builds successfully
- [ ] Application starts without errors
- [ ] API endpoints respond correctly
- [ ] Performance benchmarks meet expectations
- [ ] CI/CD pipeline passes
- [ ] Documentation updated

## 🔄 Rollback Instructions

If you need to rollback (when using automated script):

```bash
# Automatic rollback using the script
./java_upgrade.sh rollback

# Manual rollback if backup exists
cd ..
rm -rf my-project
mv java_11_backup_TIMESTAMP my-project
cd my-project
```

## 📚 Additional Resources

- [Java 21 Release Notes](https://openjdk.org/projects/jdk/21/)
- [Java 21 New Features](https://openjdk.org/jeps/0)
- [Spring Boot 3.x Migration Guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)
- [Maven Compiler Plugin](https://maven.apache.org/plugins/maven-compiler-plugin/)
- [Gradle Java Toolchain](https://docs.gradle.org/current/userguide/toolchains.html)

## 🤖 Using the AI DevOps Agent

You can always trigger the AI DevOps Agent for Java upgrades:

```bash
# From your project root
python3 src/main.py "Upgrade Java from version 11 to 21"

# Or create a Jira ticket with Java upgrade requirements
# and share the ticket: jira: YOUR-TICKET-ID
```

## 📞 Support

If you encounter issues:
1. Check the comprehensive guide: `java_upgrade_guide.md`
2. Review example configurations in the workspace
3. Check build logs for specific errors
4. Consult Java 21 migration documentation

---

**Generated by AI DevOps Agent**  
**Branch:** feature/upgrade-AI-Devops-Agent  
**Status:** ✅ Ready for use  
**Last Updated:** $(date)
