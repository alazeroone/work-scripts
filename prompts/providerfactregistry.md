Here’s a **documentable format** summarizing the decisions and schema updates for the **`providerfactregistry`** and **`tpsvsource`** tables.

---

# **Fact Code Registry and Verification System Design**

### **Objective**
To redesign the **`providerfactregistry`** table for scalability, maintainability, and clarity, while separating the verification method details to a more appropriate table (i.e., `tpsvsource`). This restructuring improves data integrity, reduces redundancy, and makes the schema more intuitive.

---

## **1. Renaming `tproviderfacttype` to `providerfactregistry`**
The `tproviderfacttype` table was renamed to **`providerfactregistry`** to reflect its role as a registry of all facts that are verified during provider onboarding and credentialing processes. 

### **Reasoning**:
- The new name better represents the purpose of the table as a central repository for fact types used in provider verification.
- The table now maintains an incrementing ID (`factRegistryId`) to uniquely identify each fact.

---

## **2. Incrementing ID for Uniqueness**
The previous design used a generated `code` for uniqueness. To simplify this and ensure each fact type is uniquely identifiable, we introduced an **auto-incrementing primary key** (`factRegistryId`).

### **New Column**: 
- **`factRegistryId` (INT, Primary Key)**: An auto-incrementing unique identifier for each fact in the registry.

### **Reasoning**:
- This ensures a unique and simple way to identify each record in the fact registry.
- The `code` field is retained for identification but is no longer used for uniqueness.

---

## **3. Normalization of `psvName` and `psvUrl`**
To avoid redundancy in the table, we normalized **`psvName`** and **`psvUrl`** into a separate table called **`tpsvsource`**. This table stores information about the **primary source verification (PSV)**, allowing different facts to link to the same verification source.

### **`tpsvsource` Table**:
- **`psvid` (INT, Primary Key)**: Unique identifier for each primary source.
- **`psvName` (VARCHAR)**: Name of the primary source (e.g., NPPES, DEA).
- **`psvUrl` (VARCHAR)**: URL of the primary source for verification.

### **Reasoning**:
- Normalizing these fields ensures that changes to the source name or URL need to be made in only one place, reducing redundancy and improving maintainability.

---

## **4. Moving `verificationMethod` to `tpsvsource`**
The **`verificationMethod`** column, which describes how verification is performed (e.g., automatic, manual, semi-automatic), was moved from the `providerfactregistry` table to the `tpsvsource` table. This change associates the verification method with the **source** itself, rather than each individual fact.

### **New Column in `tpsvsource`**:
- **`verificationMethod` (VARCHAR)**: The method of verification, describing how the data is verified (e.g., auto, manual, semi).

### **Reasoning**:
- The verification method typically applies to the source (e.g., DEA, NPPES), not to individual facts. Moving this column to the `tpsvsource` table reduces redundancy and ensures that verification methods are logically tied to their respective sources.

---

## **5. Updated Table Schemas**

### **`providerfactregistry` Table Schema**

| Column                   | Type        | Description                                                      |
|---------------------------|-------------|------------------------------------------------------------------|
| `factRegistryId`          | INT (PK)    | Auto-incrementing unique identifier for each fact in the registry.|
| `factCode`                | VARCHAR     | Generated code for the fact (non-unique, used for identification).|
| `providerLevelType`       | VARCHAR(50) | Provider's level type (e.g., Practitioner, Group).                |
| `factCategory`            | VARCHAR(50) | High-level category of the fact (e.g., Identifier, License).      |
| `factType`                | VARCHAR(50) | Specific type of the fact (e.g., NPI, DEA, MedicalLicense).       |
| `factSubType`             | VARCHAR(50) | Subcategory of the fact (e.g., Fellowship, Cardiology).           |
| `state`                   | VARCHAR(50) | State where the fact is applicable (optional).                    |
| `country`                 | VARCHAR(50) | Country where the fact is applicable.                             |
| `primarySourceId`         | INT (FK)    | Foreign key to `tpsvsource.psvid` for primary source details.     |
| `factDescription`         | TEXT        | Detailed description of the fact.                                 |

### **`tpsvsource` Table Schema**

| Column                   | Type        | Description                                                      |
|---------------------------|-------------|------------------------------------------------------------------|
| `psvid`                   | INT (PK)    | Auto-incrementing unique identifier for the primary source.       |
| `psvName`                 | VARCHAR(255)| Name of the primary source (e.g., NPPES, DEA, IRS).               |
| `psvUrl`                  | VARCHAR(255)| URL of the primary source for verification.                       |
| `verificationMethod`      | VARCHAR(50) | Method of verification (e.g., auto, manual, semi).                |

---

## **6. SQL Commands for Implementation**

### **Renaming `tproviderfacttype` to `providerfactregistry`**:
```sql
ALTER TABLE tproviderfacttype RENAME TO providerfactregistry;
```

### **Adding Incrementing ID for Uniqueness**:
```sql
ALTER TABLE providerfactregistry ADD COLUMN factRegistryId INT AUTO_INCREMENT PRIMARY KEY;
```

### **Creating `tpsvsource` Table**:
```sql
CREATE TABLE tpsvsource (
    psvid INT PRIMARY KEY AUTO_INCREMENT,
    psvName VARCHAR(255),
    psvUrl VARCHAR(255),
    verificationMethod VARCHAR(50)
);
```

### **Updating `providerfactregistry` to Reference `tpsvsource`**:
```sql
ALTER TABLE providerfactregistry ADD COLUMN primarySourceId INT;
ALTER TABLE providerfactregistry ADD CONSTRAINT fk_psvid FOREIGN KEY (primarySourceId) REFERENCES tpsvsource(psvid);
```

### **Removing `verificationMethod` from `providerfactregistry`**:
```sql
ALTER TABLE providerfactregistry DROP COLUMN verificationMethod;
```

---

## **Conclusion**
This redesign of the **`providerfactregistry`** and **`tpsvsource`** tables ensures:
- Improved **scalability** and **data integrity**.
- **Normalization** of primary source verification details.
- Clear, logical association between **verification methods** and their corresponding **sources**.
- Simplified management of facts related to provider onboarding and credentialing.

This structure provides a scalable and maintainable approach to handling fact verification during provider onboarding and credentialing, while also allowing for easy updates and extensions as new verification sources or methods are added.

---

Let me know if Here’s the **final document** that incorporates everything we’ve discussed, including the breakdown of facts, subtypes, and the updated estimation of possible records for each provider level.

---

# **Provider Fact Registry Documentation**

### **Overview**

The **Provider Fact Registry** is a central repository for storing all the facts verified during provider onboarding and credentialing processes. It organizes facts into **categories**, **types**, and (optionally) **subtypes**, allowing for a scalable and maintainable structure. This documentation also includes the estimation of total possible records, considering provider levels and subtypes.

---

## **1. Provider Fact Registry Schema**

| Column                   | Type        | Description                                                      |
|---------------------------|-------------|------------------------------------------------------------------|
| `factRegistryId`          | INT (PK)    | Auto-incrementing unique identifier for each fact in the registry.|
| `factCode`                | VARCHAR     | Generated code for the fact (non-unique, used for identification).|
| `providerLevelType`       | VARCHAR(50) | Provider's level type (e.g., Practitioner, Group, Facility, Organization).|
| `factCategory`            | VARCHAR(50) | High-level category of the fact (e.g., Identifier, License).      |
| `factType`                | VARCHAR(50) | Specific type of the fact (e.g., NPI, DEA, MedicalLicense).       |
| `factSubType`             | VARCHAR(50) | Subcategory of the fact (e.g., Fellowship, Cardiology).           |
| `state`                   | VARCHAR(50) | State where the fact is applicable (optional).                    |
| `country`                 | VARCHAR(50) | Country where the fact is applicable.                             |
| `primarySourceId`         | INT (FK)    | Foreign key to `tpsvsource.psvid` for primary source details.     |
| `factDescription`         | TEXT        | Detailed description of the fact.                                 |

---

## **2. Hierarchical Breakdown of Fact Categories, Types, and Subtypes**

This section details the hierarchical structure of **factCategory**, **factType**, and **factSubType**, helping to ensure consistency when populating the provider fact registry.

| **factCategory**  | **factType**        | **factSubType**         | **Description**                                              |
|-------------------|---------------------|-------------------------|--------------------------------------------------------------|
| **Identifier**     | NPI                 | *(None)*                 | National Provider Identifier (NPI)                           |
| **Identifier**     | DEA                 | *(None)*                 | Drug Enforcement Administration (DEA) license                |
| **Identifier**     | TIN                 | *(None)*                 | Tax Identification Number                                    |
| **Identifier**     | FedTaxID            | *(None)*                 | Federal Tax Identification Number                            |
| **License**        | MedicalLicense      | INDLICTYP                | Medical License with individual license type (e.g., Physician, Surgeon) |
| **License**        | NursingLicense      | *(None)*                 | Nursing License                                               |
| **Certification**  | SpecialtyBoard      | Cardiology, Oncology, Pediatrics | Specialty board certification in various specialties       |
| **Certification**  | CPR                 | *(None)*                 | CPR certification                                             |
| **Education**      | MedicalTraining     | Fellowship, Residency    | Fellowship and Residency training programs                    |
| **Education**      | MedicalSchool       | *(None)*                 | Medical school graduation                                     |
| **WorkExperience** | HospitalExperience  | *(None)*                 | Work experience in a hospital                                 |

---

## **3. Summary of Facts by Provider Level**

### **3.1 Practitioner**

| **factCategory**  | **factType**        | **factSubType**         | **Total Subtypes**  | **Description**                              |
|-------------------|---------------------|-------------------------|---------------------|----------------------------------------------|
| **Identifier**     | NPI                 | *(None)*                 | 1                   | National Provider Identifier (NPI)           |
| **Identifier**     | DEA                 | *(None)*                 | 1                   | DEA License                                  |
| **Identifier**     | FedTaxID            | *(None)*                 | 1                   | Federal Tax Identification Number            |
| **License**        | MedicalLicense      | INDLICTYP                | 3                   | Medical License with individual license types (e.g., Physician, Surgeon, Dentist) |
| **License**        | NursingLicense      | *(None)*                 | 1                   | Nursing License                              |
| **Certification**  | SpecialtyBoard      | Cardiology, Oncology, Pediatrics | 3         | Specialty board certifications in various fields |
| **Certification**  | CPR                 | *(None)*                 | 1                   | CPR certification                            |
| **Education**      | MedicalTraining     | Fellowship, Residency    | 2                   | Fellowship and Residency programs            |
| **Education**      | MedicalSchool       | *(None)*                 | 1                   | Medical school graduation                    |
| **WorkExperience** | HospitalExperience  | *(None)*                 | 1                   | Work experience in hospitals                 |

### **3.2 Group**

| **factCategory**  | **factType**        | **factSubType**         | **Total Subtypes**  | **Description**                              |
|-------------------|---------------------|-------------------------|---------------------|----------------------------------------------|
| **Identifier**     | TIN                 | *(None)*                 | 1                   | Tax Identification Number (TIN)              |
| **Identifier**     | FedTaxID            | *(None)*                 | 1                   | Federal Tax Identification Number            |
| **License**        | GroupLicense        | *(None)*                 | 1                   | Group operating license                      |

### **3.3 Facility**

| **factCategory**  | **factType**        | **factSubType**         | **Total Subtypes**  | **Description**                              |
|-------------------|---------------------|-------------------------|---------------------|----------------------------------------------|
| **Identifier**     | NPI                 | *(None)*                 | 1                   | National Provider Identifier (NPI)           |
| **Identifier**     | FedTaxID            | *(None)*                 | 1                   | Federal Tax Identification Number            |
| **License**        | FacilityLicense     | *(None)*                 | 1                   | Facility operating license                   |
| **WorkExperience** | FacilityExperience  | *(None)*                 | 1                   | Facility work experience                     |

### **3.4 Organization**

| **factCategory**  | **factType**        | **factSubType**         | **Total Subtypes**  | **Description**                              |
|-------------------|---------------------|-------------------------|---------------------|----------------------------------------------|
| **Identifier**     | FedTaxID            | *(None)*                 | 1                   | Federal Tax Identification Number            |
| **License**        | OrganizationLicense | *(None)*                 | 1                   | Organizational license                       |
| **Certification**  | OrganizationCert    | *(None)*                 | 1                   | Certifications for the organization          |
| **WorkExperience** | OrgWorkExperience   | *(None)*                 | 1                   | Organizational work experience               |

---

## **4. Estimation of Total Possible Records**

We have calculated the number of possible records based on **providerLevelType**, **factCategory**, **factType**, **factSubType**, and the number of **states** (50 U.S. states + 1 for non-state-specific facts). We also consider **8 possible primary sources**.

#### **Estimated Total Records by Provider Level**

| **Provider Level** | **Total Facts (with Subtypes)** | **Calculation**                                | **Estimated Records** |
|--------------------|---------------------------------|------------------------------------------------|-----------------------|
| Practitioner        | 15                              | 15 facts × 51 states × 8 sources               | 6,120                 |
| Group               | 3                               | 3 facts × 51 states × 8 sources                | 1,224                 |
| Facility            | 4                               | 4 facts × 51 states × 8 sources                | 1,632                 |
| Organization        | 4                               | 4 facts × 51 states × 8 sources                | 1,632                 |

### **Total Estimated Records**: **10,608**

This estimate reflects the potential number of records across all **providerLevelTypes** after accounting for **subtypes** for certain fact types.

---

## **5. PSV Source Table**

The **`tpsvsource`** table holds the primary source verification (PSV) details. This table is normalized to reduce redundancy in the provider fact registry.

| Column                   | Type        | Description                                                      |
|---------------------------|-------------|------------------------------------------------------------------|
| `psvid`                   | INT (PK)    | Auto-incrementing unique identifier for the primary source.       |
| `psvName`                 | VARCHAR(255)| Name of the primary source (e.g., NPPES, DEA, IRS).               |
| `psvUrl`                  | VARCHAR(255)| URL of the primary source for verification.                       |
| `verificationMethod`      | VARCHAR(50) | Method of verification (e.g., auto, manual, semi).                |

---

## **6. Example Records**

### **Example Records for `providerfactregistry`**

| factRegistryId | factCode                               | providerLevelType | factCategory   | factType        | factSubType      | state | country | primarySourceId | factDescription                                                   |
|----------------|----------------------------------------|-------------------|----------------|-----------------|------------------|-------|---------|----------------|-------------------------------------------------------------------|
| 1              | Practitioner_NPI_NY_USA                | Practitioner      | Identifier     |

 NPI             |                  | NY    | USA     | 1              | National Provider Identifier (NPI) verification for New York.     |
| 2              | Practitioner_DEA_CA_USA                | Practitioner      | Identifier     | DEA             |                  | CA    | USA     | 2              | DEA license verification for controlled substances in California. |
| 3              | Practitioner_MedicalLicense_CA_USA     | Practitioner      | License        | MedicalLicense  | INDLICTYP        | CA    | USA     | 3              | Medical license verification for physicians in California.        |
| 4              | Group_TIN_USA                          | Group             | Identifier     | TIN             |                  |       | USA     | 6              | Federal Tax Identification Number (TIN) for groups in the USA.    |
| 5              | Practitioner_SpecialtyBoard_Cardiology_FL_USA | Practitioner  | Certification | SpecialtyBoard  | Cardiology       | FL    | USA     | 5              | Cardiology board certification verification in Florida.           |

### **Example Records for `tpsvsource`**

| psvid | psvName                   | psvUrl                                   | verificationMethod |
|-------|---------------------------|------------------------------------------|--------------------|
| 1     | NPPES                      | https://npiregistry.cms.hhs.gov          | auto               |
| 2     | DEA Diversion Control       | https://www.deadiversion.usdoj.gov       | semi               |
| 3     | Medical Board of California | https://www.mbc.ca.gov                   | manual             |
| 6     | IRS                        | https://www.irs.gov                      | manual             |
| 5     | ABIM                       | https://www.abim.org                     | auto               |

---

### **Conclusion**

The **Provider Fact Registry** documentation has been updated to include:
- A detailed breakdown of facts, types, and subtypes for each **providerLevelType**.
- The revised estimation of total possible records (**10,608**) based on subtypes and relevant facts for each provider level.
- A hierarchical breakdown of facts and example records for both the **providerfactregistry** and **tpsvsource** tables.

This structured documentation helps in managing the provider onboarding and credentialing process effectively.

---

Let me know if this final document covers everything or if any additional 
 changes are needed! documentation format works for you or if you’d like to add any further details!


Here’s the **final document** that incorporates everything we’ve discussed, including the breakdown of facts, subtypes, and the updated estimation of possible records for each provider level.

---

# **Provider Fact Registry Documentation**

### **Overview**

The **Provider Fact Registry** is a central repository for storing all the facts verified during provider onboarding and credentialing processes. It organizes facts into **categories**, **types**, and (optionally) **subtypes**, allowing for a scalable and maintainable structure. This documentation also includes the estimation of total possible records, considering provider levels and subtypes.

---

## **1. Provider Fact Registry Schema**

| Column                   | Type        | Description                                                      |
|---------------------------|-------------|------------------------------------------------------------------|
| `factRegistryId`          | INT (PK)    | Auto-incrementing unique identifier for each fact in the registry.|
| `factCode`                | VARCHAR     | Generated code for the fact (non-unique, used for identification).|
| `providerLevelType`       | VARCHAR(50) | Provider's level type (e.g., Practitioner, Group, Facility, Organization).|
| `factCategory`            | VARCHAR(50) | High-level category of the fact (e.g., Identifier, License).      |
| `factType`                | VARCHAR(50) | Specific type of the fact (e.g., NPI, DEA, MedicalLicense).       |
| `factSubType`             | VARCHAR(50) | Subcategory of the fact (e.g., Fellowship, Cardiology).           |
| `state`                   | VARCHAR(50) | State where the fact is applicable (optional).                    |
| `country`                 | VARCHAR(50) | Country where the fact is applicable.                             |
| `primarySourceId`         | INT (FK)    | Foreign key to `tpsvsource.psvid` for primary source details.     |
| `factDescription`         | TEXT        | Detailed description of the fact.                                 |

---

## **2. Hierarchical Breakdown of Fact Categories, Types, and Subtypes**

This section details the hierarchical structure of **factCategory**, **factType**, and **factSubType**, helping to ensure consistency when populating the provider fact registry.

| **factCategory**  | **factType**        | **factSubType**         | **Description**                                              |
|-------------------|---------------------|-------------------------|--------------------------------------------------------------|
| **Identifier**     | NPI                 | *(None)*                 | National Provider Identifier (NPI)                           |
| **Identifier**     | DEA                 | *(None)*                 | Drug Enforcement Administration (DEA) license                |
| **Identifier**     | TIN                 | *(None)*                 | Tax Identification Number                                    |
| **Identifier**     | FedTaxID            | *(None)*                 | Federal Tax Identification Number                            |
| **License**        | MedicalLicense      | INDLICTYP                | Medical License with individual license type (e.g., Physician, Surgeon) |
| **License**        | NursingLicense      | *(None)*                 | Nursing License                                               |
| **Certification**  | SpecialtyBoard      | Cardiology, Oncology, Pediatrics | Specialty board certification in various specialties       |
| **Certification**  | CPR                 | *(None)*                 | CPR certification                                             |
| **Education**      | MedicalTraining     | Fellowship, Residency    | Fellowship and Residency training programs                    |
| **Education**      | MedicalSchool       | *(None)*                 | Medical school graduation                                     |
| **WorkExperience** | HospitalExperience  | *(None)*                 | Work experience in a hospital                                 |

---

## **3. Summary of Facts by Provider Level**

### **3.1 Practitioner**

| **factCategory**  | **factType**        | **factSubType**         | **Total Subtypes**  | **Description**                              |
|-------------------|---------------------|-------------------------|---------------------|----------------------------------------------|
| **Identifier**     | NPI                 | *(None)*                 | 1                   | National Provider Identifier (NPI)           |
| **Identifier**     | DEA                 | *(None)*                 | 1                   | DEA License                                  |
| **Identifier**     | FedTaxID            | *(None)*                 | 1                   | Federal Tax Identification Number            |
| **License**        | MedicalLicense      | INDLICTYP                | 3                   | Medical License with individual license types (e.g., Physician, Surgeon, Dentist) |
| **License**        | NursingLicense      | *(None)*                 | 1                   | Nursing License                              |
| **Certification**  | SpecialtyBoard      | Cardiology, Oncology, Pediatrics | 3         | Specialty board certifications in various fields |
| **Certification**  | CPR                 | *(None)*                 | 1                   | CPR certification                            |
| **Education**      | MedicalTraining     | Fellowship, Residency    | 2                   | Fellowship and Residency programs            |
| **Education**      | MedicalSchool       | *(None)*                 | 1                   | Medical school graduation                    |
| **WorkExperience** | HospitalExperience  | *(None)*                 | 1                   | Work experience in hospitals                 |

### **3.2 Group**

| **factCategory**  | **factType**        | **factSubType**         | **Total Subtypes**  | **Description**                              |
|-------------------|---------------------|-------------------------|---------------------|----------------------------------------------|
| **Identifier**     | TIN                 | *(None)*                 | 1                   | Tax Identification Number (TIN)              |
| **Identifier**     | FedTaxID            | *(None)*                 | 1                   | Federal Tax Identification Number            |
| **License**        | GroupLicense        | *(None)*                 | 1                   | Group operating license                      |

### **3.3 Facility**

| **factCategory**  | **factType**        | **factSubType**         | **Total Subtypes**  | **Description**                              |
|-------------------|---------------------|-------------------------|---------------------|----------------------------------------------|
| **Identifier**     | NPI                 | *(None)*                 | 1                   | National Provider Identifier (NPI)           |
| **Identifier**     | FedTaxID            | *(None)*                 | 1                   | Federal Tax Identification Number            |
| **License**        | FacilityLicense     | *(None)*                 | 1                   | Facility operating license                   |
| **WorkExperience** | FacilityExperience  | *(None)*                 | 1                   | Facility work experience                     |

### **3.4 Organization**

| **factCategory**  | **factType**        | **factSubType**         | **Total Subtypes**  | **Description**                              |
|-------------------|---------------------|-------------------------|---------------------|----------------------------------------------|
| **Identifier**     | FedTaxID            | *(None)*                 | 1                   | Federal Tax Identification Number            |
| **License**        | OrganizationLicense | *(None)*                 | 1                   | Organizational license                       |
| **Certification**  | OrganizationCert    | *(None)*                 | 1                   | Certifications for the organization          |
| **WorkExperience** | OrgWorkExperience   | *(None)*                 | 1                   | Organizational work experience               |

---

## **4. Estimation of Total Possible Records**

We have calculated the number of possible records based on **providerLevelType**, **factCategory**, **factType**, **factSubType**, and the number of **states** (50 U.S. states + 1 for non-state-specific facts). We also consider **8 possible primary sources**.

#### **Estimated Total Records by Provider Level**

| **Provider Level** | **Total Facts (with Subtypes)** | **Calculation**                                | **Estimated Records** |
|--------------------|---------------------------------|------------------------------------------------|-----------------------|
| Practitioner        | 15                              | 15 facts × 51 states × 8 sources               | 6,120                 |
| Group               | 3                               | 3 facts × 51 states × 8 sources                | 1,224                 |
| Facility            | 4                               | 4 facts × 51 states × 8 sources                | 1,632                 |
| Organization        | 4                               | 4 facts × 51 states × 8 sources                | 1,632                 |

### **Total Estimated Records**: **10,608**

This estimate reflects the potential number of records across all **providerLevelTypes** after accounting for **subtypes** for certain fact types.

---

## **5. PSV Source Table**

The **`tpsvsource`** table holds the primary source verification (PSV) details. This table is normalized to reduce redundancy in the provider fact registry.

| Column                   | Type        | Description                                                      |
|---------------------------|-------------|------------------------------------------------------------------|
| `psvid`                   | INT (PK)    | Auto-incrementing unique identifier for the primary source.       |
| `psvName`                 | VARCHAR(255)| Name of the primary source (e.g., NPPES, DEA, IRS).               |
| `psvUrl`                  | VARCHAR(255)| URL of the primary source for verification.                       |
| `verificationMethod`      | VARCHAR(50) | Method of verification (e.g., auto, manual, semi).                |

---

## **6. Example Records**

### **Example Records for `providerfactregistry`**

| factRegistryId | factCode                               | providerLevelType | factCategory   | factType        | factSubType      | state | country | primarySourceId | factDescription                                                   |
|----------------|----------------------------------------|-------------------|----------------|-----------------|------------------|-------|---------|----------------|-------------------------------------------------------------------|
| 1              | Practitioner_NPI_NY_USA                | Practitioner      | Identifier     |

 NPI             |                  | NY    | USA     | 1              | National Provider Identifier (NPI) verification for New York.     |
| 2              | Practitioner_DEA_CA_USA                | Practitioner      | Identifier     | DEA             |                  | CA    | USA     | 2              | DEA license verification for controlled substances in California. |
| 3              | Practitioner_MedicalLicense_CA_USA     | Practitioner      | License        | MedicalLicense  | INDLICTYP        | CA    | USA     | 3              | Medical license verification for physicians in California.        |
| 4              | Group_TIN_USA                          | Group             | Identifier     | TIN             |                  |       | USA     | 6              | Federal Tax Identification Number (TIN) for groups in the USA.    |
| 5              | Practitioner_SpecialtyBoard_Cardiology_FL_USA | Practitioner  | Certification | SpecialtyBoard  | Cardiology       | FL    | USA     | 5              | Cardiology board certification verification in Florida.           |

### **Example Records for `tpsvsource`**

| psvid | psvName                   | psvUrl                                   | verificationMethod |
|-------|---------------------------|------------------------------------------|--------------------|
| 1     | NPPES                      | https://npiregistry.cms.hhs.gov          | auto               |
| 2     | DEA Diversion Control       | https://www.deadiversion.usdoj.gov       | semi               |
| 3     | Medical Board of California | https://www.mbc.ca.gov                   | manual             |
| 6     | IRS                        | https://www.irs.gov                      | manual             |
| 5     | ABIM                       | https://www.abim.org                     | auto               |

---

### **Conclusion**

The **Provider Fact Registry** documentation has been updated to include:
- A detailed breakdown of facts, types, and subtypes for each **providerLevelType**.
- The revised estimation of total possible records (**10,608**) based on subtypes and relevant facts for each provider level.
- A hierarchical breakdown of facts and example records for both the **providerfactregistry** and **tpsvsource** tables.

This structured documentation helps in managing the provider onboarding and credentialing process effectively.

---

Let me know if this final document covers everything or if any additional changes are needed!
