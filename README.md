# Agentic Trip Planner 🌍✈️

Welcome to the **Agentic Trip Planner**, an intelligent, interactive application that helps you plan, explore, and compare travel destinations. Leveraging the power of LangGraph agents on the backend, this platform provides curated itineraries, activity recommendations, accommodation suggestions, and more!

## 🚀 Features
- **Conversational Trip Planning**: Chat with an AI assistant to tailor a trip exactly to your preferences.
- **Agentic Workflows**: Powered by specialized LangGraph agents (Activities, Accommodations, Itinerary, Maps, Weather, Email, etc.) acting harmoniously under a Supervisor agent.
- **Destination Comparison**: Side-by-side breakdown of locations to help you decide your next adventure.
- **Detailed Itineraries**: Get day-by-day breakdowns with activities, travel logistics, and estimated costs.
- **Modern UI**: A responsive, beautifully designed frontend interface.

## 🛠️ Tech Stack
- **Frontend**: React.js, React Router, Axios, Lucide React
- **Backend**: Python, FastAPI, LangGraph, MongoDB / SQLite
- **AI Integration**: LangChain, LLMs (for intelligent agent-based planning)

---

## ⚙️ Prerequisites
Ensure you have the following installed on your local machine:
- **Node.js** (v16 or higher) and npm
- **Python** (v3.9 or higher)
- **Git**

---

## 🏗️ Local Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/adityapwr87/Trip-Planner-Agent.git
cd Trip-Planner-Agent
```

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure Environment Variables:
   - Create a `.env` file in the `backend` folder.
   - Add your necessary API keys (e.g., LLM provider keys, Database URIs, etc.).
5. Run the FastAPI development server:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
   *The backend will be available at `http://localhost:8000`*

### 3. Frontend Setup
1. Open a new terminal tab/window and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the Node dependencies:
   ```bash
   npm install
   ```
3. Start the React development server:
   ```bash
   npm start
   ```
   *The frontend will be available at `http://localhost:3000`*

---

## 📖 Usage
Once both the backend and frontend are running:
1. Open your browser to `http://localhost:3000`.
2. Sign up or log in to your account.
3. Start chatting with the trip planner agent or explore destinations using the dashboard.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to contribute.

## 📝 License
This project is open-source and available under the MIT License.
