# Asset Valuation Service

## Overview

The **Asset Valuation Service** is an asynchronous worker that plays a crucial role in the risk assessment pipeline. It consumes `asset.discovered` events from Kafka. For each discovered asset, this service applies the quantitative valuation methodology defined in the project's core documentation.

Specifically, it calculates scores for **Confidentiality, Integrity, and Availability (CIA)** and then aggregates them into a final **Quantitative Asset Score (SCA)**. This score represents the asset's importance and value to the organization.

After calculating the value, the service updates the asset's record in the database and publishes an `asset.valuated` event to Kafka, passing the baton to the next stage of the pipeline (Vulnerability Scanning).

## Tech Stack

- **Language:** Python 3.11+
- **Messaging:** Apache Kafka
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Containerization:** Docker

## Core Logic: CIA/SCA Calculation

This service automates the "Cuestionario de Valoración CIA" from the project methodology. Since direct user input is not available in an automated flow, the `CIACalculatorService` uses a **heuristic-based approach** to assign initial metric scores. For example, an asset with "api" in its name is given higher Confidentiality and Availability scores by default.

The final scores are calculated using the formulas:
- `Score_Dimension = (SUM(metric_scores) / num_metrics) * 10`
- `SCA = (SCA_C + SCA_I + SCA_D) / 3`

## Architecture

This service is a "headless" worker with no API. It adheres to **Clean Architecture**:

1.  **Domain:** Defines the `Asset` entity (including its value attributes) and the abstract repository interfaces.
2.  **Application:** Contains the `ValueAssetUseCase` and the core `CIACalculatorService`.
3.  **Infrastructure:** Provides concrete implementations for the PostgreSQL repository and Kafka producer.
4.  **Worker:** The main process that runs the Kafka consumer and orchestrates the use case execution.

## Getting Started

Follow the standard procedure: clone, create a virtual environment, install dependencies from `requirements.txt`, configure your `.env` file, and run `python main.py`.

## Disclaimer

This service is intended solely for educational and research purposes within authorized environments. It must **not** be used against systems, networks, or digital assets without explicit permission from their owners.

The valuation logic applied in this microservice is based on heuristic assumptions and simplified models; therefore, it should **not** be considered a substitute for a comprehensive risk assessment conducted by certified professionals.

Users are fully responsible for any consequences arising from improper or unauthorized use. Always adhere to ethical principles and local cybersecurity laws when deploying or modifying this tool.
