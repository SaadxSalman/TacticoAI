# Fin-Agent 💰📈

A multi-agent system that autonomously monitors financial markets, reads news articles, and analyzes sentiment to make predictions and generate reports. Fin-Agent acts as a personal financial advisor, with a strong focus on risk management and data-driven insights.

-----

## ✨ Features

  * **Autonomous Market Monitoring:** The **Data Retrieval Agent** autonomously pulls and processes real-time financial market data and news.
  * **Sentiment and News Analysis:** The **Sentiment Analysis Agent** reads news articles and social media to gauge market sentiment, providing a crucial leading indicator.
  * **Predictive Modeling:** The **Modeling Agent** runs complex simulations and analyzes historical data to generate predictions and identify potential risks.
  * **Comprehensive Reporting:** The **Reporting Agent** synthesizes all findings into clear and concise reports, making complex financial data accessible to the user.
  * **Chart and Graph Interpretation:** Utilizes a **vision model** to interpret charts and graphs directly from financial reports, adding a powerful layer of visual data analysis.
  * **Specialized Knowledge:** Employs a specialized **embedding model** fine-tuned on financial news and SEC filings for highly accurate and contextually relevant analysis.

-----

## ⚙️ Tech Stack

  * **Frontend:** [Next.js](https://nextjs.org/)
  * **Communication:** tRPC
  * **Core Analysis Model:** Massive language model
  * **Vector Search:** [Qdrant](https://qdrant.tech/)
  * **Time-Series Database:** Custom time-series database

-----

## 🚀 Getting Started

### Prerequisites

  * Node.js (for Next.js)
  * Python 3.10+ (for backend services and models)
  * Docker (for the time-series database and Qdrant)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/saadsalmanakram/Fin-Agent.git
    cd Fin-Agent
    ```
2.  **Start Docker containers:**
    ```bash
    docker-compose up -d
    ```
3.  **Set up the frontend and backend:**
    Follow the instructions in the `frontend/` and `backend/` directories to install dependencies and configure the services.

### Configuration

Create a `.env` file to store your API keys for financial data providers and other necessary environment variables.

### Usage

Run the Next.js server and the backend agent services to begin autonomous market monitoring and reporting.

-----

## 🤝 Contributing

We welcome contributions from financial analysts, data scientists, and developers. Please read our [CONTRIBUTING.md](https://www.google.com/search?q=https://github.com/saadsalmanakram/Fin-Agent/blob/main/CONTRIBUTING.md) for details on submitting pull requests.

-----

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=https://github.com/saadsalmanakram/Fin-Agent/blob/main/LICENSE) file for details.
