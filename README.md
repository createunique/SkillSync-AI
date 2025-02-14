# SkillSync AI

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Architecture and Design](#architecture-and-design)
- [Advanced Configuration & Troubleshooting](#advanced-configuration--troubleshooting)
- [Testing and Contribution Guidelines](#testing-and-contribution-guidelines)
- [License and Acknowledgments](#license-and-acknowledgments)

## Project Overview

SkillSync AI is a web-based application aimed at streamlining candidate screening by leveraging artificial intelligence to compare resumes with job descriptions. The project integrates Streamlit for the frontend, Firebase for authentication and real-time data logging, and OpenAI for evaluation and Q&A generation. Its target audience includes HR professionals, recruitment teams, and talent acquisition specialists looking to optimize their hiring process.

## Features

- **Resume Evaluation**: Upload resumes (PDF, DOCX, TXT) and automatically assess compatibility with a job description.
- **Interview Q&A Generation**: Generate technical interview questions and concise model answers based on candidate data.
- **Dashboard Analytics**: Visualize user analytics, resume evaluation statistics, and download results as CSV.
- **User Authentication**: Secure login using Google OAuth, restricted to approved email domains.
- **File Extraction Utilities**: Extract text seamlessly from multiple file formats.
- **Firebase Integration**: Store user data, track usage, and maintain real-time logs.
- **Modular and Scalable Design**: Clean separation of concerns to support future enhancements.

## Installation and Setup

1. **Clone the Repository**

   ```bash
   git clone <repository_url>
   cd SkillSync_AI
   ```

2. **Create and Activate a Virtual Environment**

   ```bash
   python -m venv venv
   # On Unix or MacOS:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   _Ensure Python 3.7+ is installed._

4. **Configure Environment Variables**

   - Create a `.env` file in the project root:
     ```
     API_KEY=your_openai_api_key_here
     ```

5. **Firebase & OAuth Setup**

   - Place your Firebase configuration file at:
     `/c:/Users/{username}/Downoads/SkillSync_AI/config/firebase.json`
   - Place your OAuth client secrets at:
     `/c:/Users/{username}/Downloads/SkillSync_AI/config/client_secret.json`

6. **Run the Application**
   ```bash
   streamlit run src/app.py
   ```

## Usage

- **Authentication**: Users begin by signing in with Google. Only emails ending in `@companyemail.com` (configurable) are granted access.
- **Resume Analysis Flow**:
  1. Input the job description.
  2. Upload candidate resumes in supported file formats.
  3. Click "Evaluate Resumes" to receive automatic scoring.
  4. Review the ranking and download CSV reports.
  5. For interview preparation, select a candidate and generate related interview Q&A.
- **Admin Dashboard**: Administrators access detailed analytics including user login counts, resume processing numbers, and usage statistics.

## Project Structure

- **/src**
  - `app.py`: Entry point for the Streamlit application.
  - `authentication.py`: Manages user login, logout, and Firebase operations.
  - `resume_analysis.py`: Handles resume evaluation and interview Q&A generation.
  - `utils.py`: Provides helper functions for file content extraction.
- **/config**
  - `firebase.json`: Firebase service account configuration.
  - `client_secret.json`: OAuth client secrets for Google authentication.
- **.gitignore**: Lists folders and files to ignore in version control.
- **README.md**: Provides detailed documentation and usage instructions.

## Architecture and Design

SkillSync AI is built on a modular architecture:

- **Frontend**: Developed with Streamlit, offering an interactive and responsive user interface.
- **Backend**: Utilizes Firebase for secure user management and real-time logging, and integrates OpenAI’s API to perform AI-powered resume evaluations.
- **Design Patterns**: Employs separation of concerns by distributing functions across dedicated modules (authentication, resume analysis, utilities).
- **Scalability & Maintenance**: Structured to handle increasing data loads and frequent updates, ensuring the platform remains robust and secure.

## Advanced Configuration & Troubleshooting

- **Environment Configuration**: Verify that the `.env` file contains the correct OpenAI API key. Missing or incorrect keys will cause the application to terminate.
- **Firebase & OAuth Issues**: Ensure that configuration files for Firebase and OAuth reside in `/c:/Users/{username}/Downloads/SkillSync_AI/config/` and have valid credentials.
- **Debugging**:
  - Use Streamlit’s built-in logs to diagnose runtime errors.
  - Verify file type support in `utils.py` if encountering extraction issues.
  - Read the error messages provided by both authentication and evaluation modules for guidance.
- **Performance Tuning**: Modify `max_tokens`, `temperature`, and API model parameters in `resume_analysis.py` to suit specific recruitment needs and optimize performance.

## Testing and Contribution Guidelines

- **Running Tests**: _(When available)_ Execute tests using:
  ```bash
  pytest
  ```
- **Contributing**:
  - Fork the repository and create a feature branch.
  - Adhere to the code style and documentation conventions.
  - Submit pull requests with clear descriptions of changes and test results.
- **Reporting Issues**: Use the repository’s GitHub Issues page for bug reports, feature requests, or other feedback.

## License and Acknowledgments

- **License**: Released under the [MIT License](LICENSE).
- **Acknowledgments**:
  - Special thanks to Firebase, Streamlit, and OpenAI for their services and APIs.
  - Gratitude to our contributors and the community for continuous support and feedback.
  - Inspired by innovative recruitment solutions and AI advancements.
