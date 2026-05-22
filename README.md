# NSE Automation

Automated NSE market data pipeline built to generate structured daily datasets for tracking a specific market observation workflow.

The project is designed around automation reliability rather than manual data collection, using scheduled GitHub Actions workflows to extract, process, and export market data automatically.

## Features

* Daily automated execution using GitHub Actions
* Extraction of NSE top gainers and losers under a defined range
* Automated market-cap and share-count data processing
* Structured Excel export generation
* Master dataset building workflow
* Fully cloud-executed pipeline without local runtime dependency

## Tech Stack

* Python
* Playwright
* Pandas
* OpenPyXL
* GitHub Actions

## Workflow

1. GitHub Actions triggers the automation on schedule
2. NSE data extraction runs using Playwright
3. Processed datasets are cleaned and structured
4. Master dataset builder combines and organizes data
5. Excel exports are automatically updated and committed

## Project Structure

```text
.github/workflows/   -> GitHub Actions workflow
exports/             -> Generated daily exports
main.py              -> NSE extraction workflow
master_data_builder.py -> Dataset consolidation logic
requirements.txt     -> Python dependencies
```

## Automation Pipeline

The entire workflow runs automatically through GitHub Actions using scheduled cron execution.

Main automation tasks include:

* Environment setup
* Dependency installation
* Playwright browser setup
* NSE extraction workflow
* Dataset consolidation
* Automatic export commits

## Requirements

```bash
playwright
pandas
openpyxl
```

## Status

Active personal automation project focused on structured market-data generation and workflow experimentation.

## Workflow

1. GitHub Actions triggers the automation on schedule
2. NSE data extraction runs using Playwright
3. Processed datasets are cleaned and structured
4. Master dataset builder combines and organizes data
5. Excel exports are automatically updated and committed


