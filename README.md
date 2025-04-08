# AI-Traffic-Simulator

A visual traffic simulation and optimization system that models vehicle flow through a small urban grid of intersections. It uses Simulated Annealing, a probabilistic AI algorithm, to iteratively improve traffic light timing strategies with the goal of reducing congestion, minimizing vehicle wait times, and increasing overall throughput.

The system simulates realistic traffic behavior, tracks congestion levels, and visually shows the impact of each optimization step in real time.

![traffic ui](image.png)

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
