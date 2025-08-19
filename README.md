# Dashboard CLI Tool

A command-line dashboard for managing your degree program, modules, and exams. Analyze your study progress, track grades, and manage your academic plan interactively.

---

## Installation & Usage

### 1. Download Ready Docker Image

1. Pull the image from Docker Hub:
   ```sh
   docker pull azaleh/dashboard-cli
   ```
2. Run the CLI tool:
   ```sh
   docker run -it --rm azaleh/dashboard-cli
   ```
   - To persist your data, mount the data folder:
     ```sh
     docker run -it --rm -v "$PWD/data":/app/data azaleh/dashboard-cli
     ```

### 2. Build the Docker Image Yourself

1. Clone this repository:
   ```sh
   git clone <repo-url>
   cd dashboard
   ```
2. Build the Docker image:
   ```sh
   docker build -t dashboard-cli .
   ```
3. Run the CLI tool:
   ```sh
   docker run -it --rm dashboard-cli
   ```
   - To persist your data, mount the data folder:
     ```sh
     docker run -it --rm -v "$PWD/data":/app/data dashboard-cli
     ```

### 3. Classic Installation (Python)

1. Clone this repository:
   ```sh
   git clone <repo-url>
   cd dashboard
   ```
2. (Optional) Create and activate a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Start the CLI tool:
   ```sh
   python3 main.py
   ```

---

## How the CLI Works

- On startup, you'll see a dashboard with your current study progress and a main menu.
- You can add new modules, enter exam results, view module overviews, analyze your progress, or create a new degree program.
- The analysis option provides ECTS trends, graduation predictions, and highlights risk modules.
- All data is saved locally in the `data/` folder (by default: `data/studienverlauf.json`).
- The tool uses interactive prompts and colored output for a user-friendly experience.