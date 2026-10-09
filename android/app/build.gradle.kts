plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "nl.barry.concertagenda"
    compileSdk = 34
    defaultConfig {
        applicationId = "nl.barry.concertagenda"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
    signingConfigs {
        create("fixed") {
            storeFile = rootProject.file("debug.keystore")
            storePassword = "barrys-agenda"
            keyAlias = "barrys"
            keyPassword = "barrys-agenda"
        }
    }
    buildTypes {
        getByName("release") {
            signingConfig = signingConfigs.getByName("fixed")
            isMinifyEnabled = false
        }
        getByName("debug") { signingConfig = signingConfigs.getByName("fixed") }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.core:core-splashscreen:1.0.1")
}
