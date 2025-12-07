buildscript {
    repositories {
        // 国内镜像源 - 优先使用
        maven { url = uri("https://maven.aliyun.com/repository/google") }
        maven { url = uri("https://maven.aliyun.com/repository/gradle-plugin") }
        maven { url = uri("https://maven.aliyun.com/repository/central") }

        // 原始源作为备份（启用以获取版本信息，之后可重新注释）
        google()
        mavenCentral()
    }
    dependencies {
        classpath("com.android.tools.build:gradle:8.5.2")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.25")
    }
}

// allprojects repositories配置已移至settings.gradle中的dependencyResolutionManagement

tasks.register("clean").configure {
    delete("build")
}

