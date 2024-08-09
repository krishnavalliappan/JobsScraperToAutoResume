# LinkedIn Job Application Automation

## Overview

This project is an automated system for scraping job listings from LinkedIn, analyzing them using AI, generating tailored resumes and cover letters, and syncing the data with Notion. It's designed to streamline the job application process for job seekers.

## Features

- LinkedIn job search and scraping
- Job analysis using GPT models
- Automated resume and cover letter generation
- Notion integration for job application tracking
- Proxy rotation for enhanced web scraping reliability

- ## Usage

Run the main script to start the job application process:
`python main.py`


This will:
1. Search for jobs on LinkedIn based on the specified criteria
2. Scrape job details
3. Analyze job descriptions using AI
4. Generate tailored resumes and cover letters
5. Sync job data with Notion

## Configuration

Adjust the settings in `src/config/settings.py` to customize:
- Job search parameters
- File paths for templates and output
- Logging settings
- GPT model selection
- Notion schema

## Components

### LinkedIn Scraper

- `LinkedInScraper`: Handles login and navigation on LinkedIn
- `LinkedIn`: Manages the job search and data extraction process

### Data Processor

- `DataProcessor`: Preprocesses and analyzes job data
- `JobAnalyzer`: Uses GPT models to analyze job descriptions and generate personalized content

### Document Generator

- `ResumeManager`: Creates tailored resumes and cover letters based on job descriptions

### Notion Integration

- `NotionManager`: Syncs job application data with a Notion database

### Utilities

- `ProxyRotator`: Manages a pool of proxies for web scraping
- Various utility functions for data manipulation and URL generation

## Contributing

Contributions to this project are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Be sure to comply with LinkedIn's terms of service and respect website scraping policies.


