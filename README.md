# MTG Cobuilder API

An API service that allows users to manage Magic the Gathering collections and build decks with the assistance of an LLM Copilot-like partner.

## Features

- Manage your Magic the Gathering card collections
- Build and optimize decks with AI assistance
- Track your card inventory
- Get intelligent recommendations for deck improvements
- Analyze deck performance and statistics

## Tech Stack

- **Python 3.12**
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping
- **PostgreSQL**: Database for storing card and user data
- **Uvicorn**: ASGI server for running the API

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Poetry package manager
- PostgreSQL database

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mtgcobuilder-api.git
   cd mtgcobuilder-api
   ```

2. Initialize the project using Task:
   ```bash
   task init-project
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies
   - Set up pre-commit hooks

3. For production environments:
   ```bash
   task install-prod
   ```

### Development Setup

The project uses several development tools:

- **Ruff**: For linting and formatting
- **MyPy**: For static type checking
- **Pre-commit**: For running checks before commits

To run linters:
```bash
task lint
```

### Running the API

To start the development server:
```bash
poetry run uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once the server is running, you can access the interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Docker Deployment

A Docker Compose configuration is available in the `tests` directory for testing the full stack:

```bash
cd tests
docker-compose up
```

This will start:
- The frontend application on port 3000
- The backend API on port 8000
- A PostgreSQL database on port 5432

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.