# Profile Data: Vector Space Corpus

This directory contains the unstructured text corpora used to populate the RAG (Retrieval-Augmented Generation) engine. The data is organized hierarchically to optimize semantic retrieval.

## 📂 Directory Structure

### `CVs/`
**High-Priority Biographical Embeddings.**
-   Contains raw LaTeX source (`.tex`) and compiled PDFs (`.pdf`) of the user's Curriculum Vitae.
-   **Example**: `john_doe.tex` (The "John Doe" persona).

### `Professional_Info/`
**Chronological Employment Vectors.**
-   Detailed work history, project descriptions, and professional references.
-   **Example**: `experience.md` (Detailed role descriptions).

### `Academic_Info/`
**Educational Credential Embeddings.**
-   Transcripts, degree details, and thesis abstracts.
-   **Example**: `education.md` (PhD and BS details).

### `Personal_Info/`
**Unstructured Semantic Context.**
-   Biographical narratives, cover letter snippets, and personality traits.
-   **Example**: `bio.md` (Eccentric persona description).

### `Other_Info/`
**Auxiliary Data Points.**
-   Hobbies, manifestos, and miscellaneous context.
-   **Example**: `manifesto.md` (Personal philosophy).

## 👤 Persona: John Doe

The system is currently populated with a placeholder persona:
-   **Name**: John Doe
-   **Role**: Political AI Consultant / Computational Aesthete
-   **Affiliation**: YE2024 Campaign
-   **Location**: Cody, Wyoming
