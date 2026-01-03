# MagicResume

MagicResume is an automated tool that adapts your Curriculum Vitae (CV) to specific job offers using Artificial Intelligence (Google Gemini). The system analyzes your CV and the job offer, generates a personalized cover letter, and optimizes the CV content to highlight the most relevant skills, finally generating a new DOCX document.

No exaggeration, no false claims — only smart alignment with ATS and recruiter expectations.

## Project Architecture

The project is structured in a modular way to separate business logic, AI interaction, and file handling:

*   **`main.py`**: The application entry point. It orchestrates the entire flow: file detection, reading, communication with the API, and result generation.
*   **`file_io/`**: Module responsible for input/output operations.
    *   `document_detector.py`: Automatically detects the CV file in the input directory.
    *   `file_reader.py`: Reads the content of DOCX, ODT, or PDF files.
    *   `document_editor.py`: Applies the modifications suggested by the AI to the original DOCX file.
    *   `file_manager.py`: Manages directory creation and file copying.
*   **`llm/`**: Module for interaction with Large Language Models.
    *   `client.py`: Handles communication with the Google Gemini API.
    *   `prompt_builder.py`: Builds the instructions (prompt) sent to the model.
    *   `response_validator.py`: Validates and processes the model's JSON response.
*   **`data/`**: Input directory where the user places their documents.
*   **`outputs/`**: Directory where generated results are saved, organized by company.

## Prerequisites

*   **Python 3.10** or higher.
*   A **Google Gemini API Key** (Google AI Studio).

## Installation

1.  **Clone the repository** (if applicable) or download the source code.

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables**:
    *   Copy the example file `.env.example` and rename it to `.env`.
    *   Edit the `.env` file and add your `GEMINI_API_KEY`.

    ```ini
    GEMINI_API_KEY=your_api_key_here
    ```

## File Configuration (Data)

To run the program, you must place the input files in the `data/` folder at the project root:

1.  **Your Generic Resume**:
    *   Must be a **.docx** (Word) or **.odt** (OpenDocument) file.
    *   Place it directly inside the `data/` folder.
    *   **Important**: There should be only *one* resume file in this folder. The system will auto-detect it.

2.  **The Job Offer**:
    *   Create a text file named **`job.txt`** inside the `data/` folder.
    *   Copy and paste the full text of the job description into this file.

Expected final structure:
```
MagicResume/
├── data/
│   ├── my_base_resume.docx  <-- Your CV
│   └── job.txt              <-- The job offer
├── main.py
├── ...
```

## Execution

Once the files are configured in `data/` and the virtual environment is activated, run the following command from the terminal at the project root:

```bash
python main.py
```

## Outputs

The system will create a new folder within the `outputs/` directory with the name of the company detected in the job offer (e.g., `outputs/Google/`).

Inside, you will find:
1.  **`cover_letter.txt`**: A cover letter written specifically for the offer.
2.  **`[Name]_CV_[Company].docx`**: A copy of your CV with the modifications applied.


