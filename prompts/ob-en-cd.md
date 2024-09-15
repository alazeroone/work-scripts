Here’s a well-structured document based on our discussion, which you can present to stakeholders or your team. This document outlines the architectural design, the changes to the schema, and the rationale behind them. It also highlights potential improvements and risks, along with mitigation strategies.

---

# **Design Document for Provider Onboarding, Enrollment, and Credentialing System**

## **Overview**

This document outlines the architectural changes needed for moving the fact type and fact reference tables to the Enrollment domain while maintaining the fact verification and mandatory attribute configurations in their respective domains. The goal is to ensure a clear separation of responsibilities between **Onboarding**, **Enrollment**, and **Credentialing** domains, while facilitating smooth cross-domain interactions.

---

## **Domains and Responsibilities**

### **1. Onboarding Domain**
- **Purpose**: This domain is responsible for collecting and storing initial application data submitted by the provider. Once the application is approved, the data is passed to the Enrollment domain for further processing.
- **Core Entities**:
  - `tonboarding`: Stores provider onboarding information.
  - `troster`: Stores roster information associated with the provider's onboarding.
  - `tonboardingcaseheader`: Manages the onboarding case lifecycle.

### **2. Enrollment Domain**
- **Purpose**: This domain is responsible for managing provider information such as personal details, education history, work experience, and licenses. It ensures data completeness by enforcing mandatory attributes.
- **Core Entities**:
  - `tpractioner`: Stores the main provider record.
  - `tplmpractitioneridentifier`, `tpractionereducation`, `tpractionerworkexperience`: Store provider-specific facts.
  - `tFactTypeReference`: Defines the various fact types (e.g., education, work experience, licenses) and whether a fact is mandatory for enrollment.
  - `tProviderFactReference`: Links provider records to their specific fact records in different tables.
  - `tFactAttributeReference`: Defines which attributes of a fact type are mandatory during enrollment.

### **3. Credentialing Domain**
- **Purpose**: The Credentialing domain verifies the provider's submitted data to ensure compliance with regulatory or internal organizational standards. It maintains policies and rules related to fact verification.
- **Core Entities**:
  - `tcredentialing`: Manages the credentialing lifecycle for a provider.
  - `tVerificationConfig`: Defines which attributes of each fact type require verification.
  - `tcredentialingfact`: References fact data from Enrollment and tracks the status of fact verification.
  - `tcredentialingfactverification`: Tracks verification results at the attribute level.
  
---

## **Key Architectural Decisions**

### **A. Move `tFactTypeReference` and `tProviderFactReference` to the Enrollment Domain**

- **Why**: 
  - The Enrollment domain is responsible for managing provider data, making it the natural location for fact type definitions (`tFactTypeReference`) and provider fact references (`tProviderFactReference`).
  - Credentialing will use the fact definitions and provider fact references stored in Enrollment but will not manage them directly.

### **B. Maintain Fact Verification in Credentialing Domain**

- **Why**: 
  - Verification of fact attributes is an essential part of the credentialing process, which is driven by compliance and regulatory requirements. 
  - Therefore, the Credentialing domain will manage which fact attributes need to be verified.

### **C. Maintain Mandatory Attributes in Enrollment Domain**

- **Why**: 
  - The Enrollment domain is responsible for data completeness and ensuring that all necessary provider information is collected. 
  - Therefore, the Enrollment domain will manage the mandatory status of fact attributes.

---

## **Schema Changes**

### **1. Changes in the Enrollment Domain**

#### **1.1 `tFactTypeReference` (Moved to Enrollment)**
Defines the types of facts (e.g., education, work experience, licenses) that can be associated with a provider.

```sql
CREATE TABLE tFactTypeReference (
    FactTypeCode VARCHAR(50) PRIMARY KEY,
    FactTypeName VARCHAR(100),
    FactCategory VARCHAR(50),
    Description TEXT,
    IsMandatory BIT DEFAULT 0,  -- Indicates if the fact is mandatory for enrollment
    CreatedOn DATETIME DEFAULT GETDATE(),
    Status VARCHAR(20) DEFAULT 'Active'
);
```

#### **1.2 `tProviderFactReference` (Moved to Enrollment)**
Links providers to their specific fact records across different fact tables.

```sql
CREATE TABLE tProviderFactReference (
    ProviderFactReferenceID INT IDENTITY(1,1) PRIMARY KEY,
    ProviderID INT NOT NULL,  -- FK to tpractioner or provider table in Enrollment
    FactTypeCode VARCHAR(50) NOT NULL,  -- FK to tFactTypeReference
    FactTableName VARCHAR(100) NOT NULL,  -- e.g., tpractionereducation, tplmpractitioneridentifier
    FactRecordID INT NOT NULL,
    CreatedOn DATETIME DEFAULT GETDATE(),
    Status VARCHAR(20) DEFAULT 'Active',
    FOREIGN KEY (ProviderID) REFERENCES tpractioner(PractitionerID),
    FOREIGN KEY (FactTypeCode) REFERENCES tFactTypeReference(FactTypeCode)
);
```

#### **1.3 `tFactAttributeReference` (New in Enrollment)**
Defines which attributes of a fact type are mandatory for provider enrollment.

```sql
CREATE TABLE tFactAttributeReference (
    FactTypeCode VARCHAR(50),  -- FK to tFactTypeReference
    FieldName VARCHAR(100),  -- Attribute of the fact type (e.g., Degree, LicenseNumber)
    IsMandatory BIT DEFAULT 0,  -- Indicates if the attribute is mandatory for enrollment
    PRIMARY KEY (FactTypeCode, FieldName),
    FOREIGN KEY (FactTypeCode) REFERENCES tFactTypeReference(FactTypeCode)
);
```

### **2. Changes in the Credentialing Domain**

#### **2.1 `tVerificationConfig` (New in Credentialing)**
Defines which attributes of each fact type need verification during the credentialing process.

```sql
CREATE TABLE tVerificationConfig (
    FactTypeCode VARCHAR(50),  -- FK to Enrollment.tFactTypeReference
    FieldName VARCHAR(100),  -- Attribute of the fact type
    IsVerificationRequired BIT DEFAULT 0,  -- Indicates if the attribute needs verification
    PRIMARY KEY (FactTypeCode, FieldName),
    FOREIGN KEY (FactTypeCode) REFERENCES Enrollment.tFactTypeReference(FactTypeCode)
);
```

#### **2.2 `tcredentialingfact` (Updated in Credentialing)**
Tracks fact verification processes and references facts from Enrollment using `ProviderFactReferenceID`.

```sql
ALTER TABLE tcredentialingfact
ADD ProviderFactReferenceID INT NOT NULL,
    FOREIGN KEY (ProviderFactReferenceID) REFERENCES Enrollment.tProviderFactReference(ProviderFactReferenceID);
```

---

## **Process Flow and Domain Interaction**

### **1. Onboarding to Enrollment Flow**

1. **Onboarding Process**:
   - Provider submits data via an onboarding form.
   - The system validates and processes the data in the Onboarding domain.

2. **Transition to Enrollment**:
   - Once the onboarding process is complete, provider data is transferred to the Enrollment domain, where facts are stored, and attributes are validated based on the rules defined in `tFactAttributeReference`.

### **2. Enrollment to Credentialing Flow**

1. **Fact Definition and Fact Reference Management**:
   - The Enrollment domain manages fact definitions (`tFactTypeReference`) and links specific fact instances to providers (`tProviderFactReference`).
   - Credentialing references these facts when needed during the verification process.

2. **Verification Configuration**:
   - The Credentialing domain uses `tVerificationConfig` to determine which attributes of a fact need verification. It references fact definitions in Enrollment but manages its own verification policies.

3. **Fact Verification**:
   - Credentialing processes verify the necessary attributes and update the verification status in `tcredentialingfactverification`.

---

## **Potential Issues and Mitigation Strategies**

### **Issue 1: Cross-Domain Dependencies**
- **Problem**: Credentialing relies on Enrollment for fact definitions and provider fact references. If Enrollment is down, Credentialing operations may be impacted.
- **Mitigation**:
  - **Caching**: Credentialing can cache fact definitions and provider fact references to reduce dependency on live Enrollment services.
  - **High Availability**: Ensure that Enrollment services are highly available, and use fault-tolerant architecture to minimize downtime.

### **Issue 2: Data Consistency**
- **Problem**: Changes in Enrollment (e.g., new fact types, updated mandatory attributes) could affect Credentialing processes if not handled carefully.
- **Mitigation**:
  - **Event-Driven Architecture**: Use domain events to notify Credentialing whenever there is a change in Enrollment that affects fact definitions or attributes.
  - **Data Synchronization**: Ensure regular synchronization of fact definitions and rules between Enrollment and Credentialing domains.

### **Issue 3: Performance Overhead**
- **Problem**: Cross-domain calls for fact definitions or provider fact references may introduce latency.
- **Mitigation**:
  - **Optimize Queries**: Use indexes and query optimization techniques in both Enrollment and Credentialing to ensure fast data access.
  - **Batch Processing**: Where applicable, batch verification processes to minimize the number of cross-domain calls.

---

## **Recommendations for Improvement**

### **1. API-Based Communication Between Domains**
- **Implement API endpoints** for the Enrollment domain that allow the Credentialing domain to retrieve fact definitions and provider fact references. This promotes loose coupling and encapsulation of domain responsibilities.

### **2. Use Event-Driven Updates**
- **Implement event-driven mechanisms** (e.g., using a message broker like Kafka or RabbitMQ) to notify the Credentialing domain of changes in fact definitions or mandatory attributes in Enrollment. This ensures that Credentialing is always up-to-date without requiring synchronous calls.

###
