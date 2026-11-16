# FreshCart Data Engineering Pipelines: From Git to Gold

* **Name:** Vikas Choudhary
* **Roll Number:** 26pcso06
* **GitHub Repository:** https://github.com/vikas-choudhary-26pcso06/freshcart-pipelines

## Architecture
- **Git & GitHub CI:** Automated unit testing via pytest and GitHub Actions (Python 3.12).
- **Snowflake ELT:** Bronze (VARIANT JSON) -> Silver (Deduplication & SCD Type 2) -> Quarantine -> Gold (Deterministic Row Hash Merge).
- **Mage ML Pipeline:** Modular ML pipeline with @test quality gates.
- **RabbitMQ Streaming:** Topic exchange routing with robust ACK/NACK reliability.
