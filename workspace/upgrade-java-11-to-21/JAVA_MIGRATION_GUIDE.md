# Java 11 to 21 Migration Guide

## 🎯 Objective
Upgrade your Java project from version **11** to **21** with minimal downtime and risk.

## 📋 Pre-Migration Checklist

### 1. Environment Preparation
- [ ] Verify Java 21 is installed
  ```bash
  java -version  # Should show: openjdk version "21"
  ```
- [ ] Backup your project
  ```bash
  cp -r . ../project-backup-$(date +%Y%m%d)
  ```
- [ ] Review [Java 21 Release Notes](https://openjdk.org/projects/jdk/21/)
- [ ] Check library compatibility with Java 21

### 2. Dependency Analysis
Review your project dependencies for Java 21 compatibility:
- Spring Boot: Requires 3.0+ for Java 17+
- Hibernate: Upgrade to 6.x for Java 17+
- JUnit: Use JUnit 5.x
- Check [Maven Central](https://search.maven.org/) for updated versions

## 🔧 Step-by-Step Migration

### Step 1: Update Maven Configuration (pom.xml)

**Find this:**
```xml
<properties>
    <maven.compiler.source>11</maven.compiler.source>
    <maven.compiler.target>11</maven.compiler.target>
</properties>
```

** Replace with:**
```xml
<properties>
    <maven.compiler.source>21</maven.compiler.source>
    <maven.compiler.target>21</maven.compiler.target>
    <java.version>21</java.version>
</properties>
```

**Update compiler plugin:**
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.12.1</version>
    <configuration>
        <source>21</source>
        <target>21</target>
        <release>21</release>
    </configuration>
</plugin>
```

### Step 2: Update Gradle Configuration (build.gradle)

**For Groovy DSL:**
```groovy
java {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}
```

**For Kotlin DSL (build.gradle.kts):**
```kotlin
java {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}
```

### Step 3: Update Dockerfile

**Old:**
```dockerfile
FROM openjdk:11-jdk-alpine
```

**New:**
```dockerfile
FROM eclipse-temurin:21-jdk-alpine AS build
# ... build stage ...

FROM eclipse-temurin:21-jre-alpine
# ... runtime stage ...
```

### Step 4: Update CI/CD Pipeline

**GitHub Actions (.github/workflows/build.yml):**
```yaml
- name: Set up JDK 21
  uses: actions/setup-java@v4
  with:
    java-version: '21'
    distribution: 'temurin'
```

**Jenkins (Jenkinsfile):**
```groovy
tools {
    jdk 'JDK-21'
}
```

**GitLab CI (.gitlab-ci.yml):**
```yaml
image: eclipse-temurin:21-jdk
```

### Step 5: Code Changes Required

#### Removed APIs (requires code changes):

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

#### New Language Features You Can Use:


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
String message = STR."Hello, \{name}!";
```

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
docker build -t myapp:java21 .

# Test
docker run --rm myapp:java21

# Compare size
docker images | grep myapp
```

## 🧪 Integration Testing

1. **Deploy to test environment**
2. **Run full test suite**
3. **Performance testing** - Java 21 should be faster
4. **Monitor memory usage** - Check for any regressions

## 🚀 Deployment Strategy

### Option 1: Blue-Green Deployment
1. Deploy Java 21 version alongside current
2. Gradually shift traffic
3. Monitor for issues
4. Complete cutover or rollback

### Option 2: Canary Deployment
1. Deploy to small percentage of servers
2. Monitor metrics (errors, latency, throughput)
3. Gradually increase deployment
4. Rollback if issues detected

## ⚠️ Common Issues & Solutions

### Issue: "java: invalid source release: 21"
**Solution:** Maven compiler plugin too old
```xml
<plugin>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.12.1</version> <!-- Must be 3.11.0+ -->
</plugin>
```

### Issue: "java.lang.UnsupportedClassVersionError"
**Solution:** Ensure runtime JVM is Java 21+
```bash
java -version  # Verify you're running 21
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

- [Java 21 Release Notes](https://openjdk.org/projects/jdk/21/)
- [Java 21 JEPs](https://openjdk.org/jeps/0)
- [Migration Guide](https://docs.oracle.com/en/java/javase/21/migrate/)
- [Compatibility Guide](https://docs.oracle.com/en/java/javase/21/compatibility/)

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
**Date:** 2026-03-05 18:36:16
