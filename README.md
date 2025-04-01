# AI-Traffic-Simulator
Simulates traffic flow in a small urban environment and applies an AI optimization algorithm to reduce traffic congestion. It uses **Simulated Annealing** to evolve traffic light timing strategies in order to minimize average vehicle wait time at intersections.

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites
- Python 3.x installed on your system ([Download Python](https://www.python.org/downloads/))

### Setup Instructions

1. **Clone the Repository**  
   Run the following commands:  
   `git clone https://github.com/crfloyd/AI-Traffic-Simulator`  
   `cd AI-Traffic-Simulator`

2. **Create a Virtual Environment**  
   Create an isolated Python environment to manage dependencies:  
   `python -m venv venv`

3. **Activate the Virtual Environment**  
   - On Windows:  
     `venv\Scripts\activate`  
   - On macOS/Linux:  
     `source venv/bin/activate`  
   Once activated, your terminal prompt should change to indicate the virtual environment (e.g., `(venv)`).

4. **Install Dependencies**  
   Install the required Python packages listed in `requirements.txt`:  
   `pip install -r requirements.txt`

5. **Run the Project**  
   Execute the main script to start the application:  
   `python main.py`

### Deactivating the Virtual Environment
When you're done, you can deactivate the virtual environment by simply running:  
`deactivate`
