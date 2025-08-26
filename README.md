# Store Monitoring System

A Django-based store monitoring application that processes CSV data and generates comprehensive reports using asynchronous task processing with Celery.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [API Documentation](#api-documentation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)

## ✨ Features

- **CSV Data Processing**: Import and process large CSV files into database
- **Asynchronous Report Generation**: Generate reports using Celery workers
- **RESTful API**: Complete API endpoints with Swagger documentation
- **Data Management**: CRUD operations for database tables
- **Report Storage**: Generated reports stored locally with unique identifiers

## 🛠 Tech Stack

- **Framework**: Django
- **Database**: SQLite (easily configurable for PostgreSQL)
- **Task Queue**: Celery
- **API Documentation**: Swagger/OpenAPI
- **Language**: Python

## 📋 Prerequisites

Before running this application, ensure you have:

- Python 3.8 or higher
- Git
- Redis (for Celery broker)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <project-directory>
```

### 2. Set Up Remote Repository

```bash
git remote add origin <repo_url>
git pull origin master
```

### 3. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the Application

#### Terminal 1 - Django Server
```bash
python manage.py runserver
```

#### Terminal 2 - Celery Worker
```bash
celery -A loop_assignment worker -l info
```

The application will be available at `http://localhost:8000`

## 📚 API Documentation

Access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/swagger/`

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/data/` | Load CSV data into database |
| `POST` | `/trigger_report/` | Generate a new report (returns report ID) |
| `GET` | `/get_report/<report_id>/` | Retrieve generated report |
| `GET` | `/data/<table_name>/` | View table contents |
| `DELETE` | `/data/` | Clear database |

## 🎯 Usage

### Basic Workflow

1. **Load Data**: 
   ```bash
   POST http://localhost:8000/data/
   ```
   Upload CSV files to populate the database.

2. **Generate Report**:
   ```bash
   POST http://localhost:8000/trigger_report/
   ```
   Initiates asynchronous report generation. Returns a unique report ID.

3. **Retrieve Report**:
   ```bash
   GET http://localhost:8000/get_report/<report_id>/
   ```
   Download the generated report using the report ID.

4. **Monitor Data**:
   ```bash
   GET http://localhost:8000/data/<table_name>/
   ```
   View current data in specific tables (100 rows).

5. **Clear Database** (if needed):
   ```bash
   DELETE http://localhost:8000/data/
   ```

### Sample Reports

A sample report is already included in the `reports/` directory for reference.

## 📁 Project Structure

```
├── loop_assignment/          # Main Django project
├── reports/                  # Generated reports storage
├── store-monitor/            # App features 
├── store-monitoring-data/    # CSV source files (excluded)
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

**Note**: Source CSV files are stored in `store-monitoring-data/` directory but excluded from version control due to large file sizes.

## 🔮 Future Improvements

### Immediate Enhancements
- **Cron Jobs**: Implement scheduled tasks for handling rapid data changes
- **Docker Integration**: Containerize the application for easy deployment
- **PostgreSQL Migration**: Replace SQLite with PostgreSQL for better performance with larger datasets

### Advanced Features
- **AI-Powered Analytics**: Implement machine learning models for:
  - Predictive analytics
  - Market trend analysis  
  - Automated insights generation
  - Anomaly detection in store data

### Scalability
- **Message Queue Optimization**: Redis clustering for high-availability
- **Database Sharding**: Horizontal scaling for massive datasets
- **Load Balancing**: Multi-instance deployment support
- **Caching Layer**: Redis/Memcached integration for faster data retrieval

### Monitoring & Observability
- **Health Checks**: Application and dependency monitoring
- **Logging**: Structured logging with ELK stack
- **Metrics**: Performance and business metrics collection
- **Alerting**: Real-time notification system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Notes

- Ensure Redis is running before starting Celery workers
- Monitor Celery worker logs for task processing status
- Reports are stored locally in the `reports/` directory
- For production deployment, consider using PostgreSQL instead of SQLite

## 🐛 Troubleshooting

### Common Issues

1. **Celery Connection Error**: Ensure Redis is running
2. **Database Migration Issues**: Run `python manage.py migrate --run-syncdb`
3. **Port Already in Use**: Change port with `python manage.py runserver 8001`

