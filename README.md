# MC536: Database Project - Analysis of Brazilian students' scores in the Basic Education Assessment System (Saeb) in correlation with their socioeconomic status

## Project Overview
This project was developed by
<br/>[Mateus Farha Ribeiro](https://github.com/mateusfarhaa)  (252678)
<br/>[Matheus F. Scatolin](https://github.com/rafael-dosso)  (205237)
<br/>[Rafael Setton A. de Carvalho](https://github.com/lucas-lembo)  (254467)

## Database Schema Overview

The initial phase of our project involved developing both the conceptual and relational models of our relational database (PostgreSQL).
This foundation enabled us to analyze the relationships between school SAEB scores, IDEB (Basic Education Development Index) scores,
students' socioeconomic levels, and the geographical locations of these schools (capital, interior, rural, urban).

**Figure 1: Conceptual Model (ER Diagram)**
<p align="center">
  <img src="./models/Conceptual_Model.png" alt="Conceptual Database Model ERD" width="700"/>
</p>

**Figure 2: Relational (Logical) Model**
<p align="center">
  <img src="./models/Relational_Model.png" alt="Relational Database Model" width="700"/>
</p>

*(The detailed Physical Model SQL script can be found [here](./models/Physical_model.sql)).*


## Table of Contents

- [Datasets](#datasets)
  - [Original Data](#original-data)
  - [Preprocessed Data](#preprocessed-data)
- [Database Schema](#database-schema)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup and Usage](#setup-and-usage)
  - [Prerequisites](#prerequisites)
  - [Database Setup](#database-setup)
  - [Running the Code](#running-the-code)
- [Data Preprocessing](#data-preprocessing)
- [Analysis & Queries](#analysis--queries)
- [Results](#results)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Datasets

### Original Data

The raw data was sourced from Inep (Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira). The original files used for preprocessing are located in the `/datasets` directory:

*   `divulgacao_ensino_medio_escolas_2023.csv`: Contains data on school approval rates, Saeb scores, and Ideb scores for different years.
*   `INSE_2021_escolas.csv`: Contains data on the location of schools and the percentage of students in each socioeconomic classification at each level.

### Preprocessed Data

The original datasets were preprocessed (details in [`preprocessing.ipynb`](./preprocessing.ipynb)) to fit the designed database schema. The resulting cleaned CSV files, used for loading into the database, are located in the `/preprocessed_datasets` directory:

*   `desempenho_escolar.csv`
*   `indicadores_socio_economicos.csv`
