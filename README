This tool migrates data from a MySQL database to a PostgreSQL database. It dynamically creates the necessary tables in PostgreSQL based on the schema of the MySQL tables and transfers the data in batches. The migration process supports checkpointing, ensuring that the tool can resume from where it left off in case of a crash.

---

### **Features**

1. **Dynamic Table Creation**: Automatically creates PostgreSQL tables to match the MySQL schema.
2. **Batch Processing**: Migrates data in configurable batch sizes for better performance.
3. **Resumable Migration**: Uses a checkpoint file to resume migration from the last processed row in case of a failure.
4. **Environment Configuration**: Uses `.env` file for database credentials and configurations.
5. **Dockerized**: Fully containerized using Docker for ease of deployment.

---

### **Prerequisites**

- Python 3.12 or later
- Docker
- Access to the source MySQL database and target PostgreSQL database
- A `.env` file with the required configuration (see below)

---

### **Setup Instructions**

#### **1. Clone the Repository**
```bash
git clone https://github.com/abdulsaheel/mysql-pgsql-migrator
cd mysql-pgsql-migrator
```

#### **2. Create a `.env` File**

Create a file named `.env` in the project root directory and populate it with the following:

```env
MYSQL_HOST=<your-mysql-host>
MYSQL_PORT=<your-mysql-port>
MYSQL_USER=<your-mysql-user>
MYSQL_PASSWORD=<your-mysql-password>
MYSQL_DATABASE=<your-mysql-database>

POSTGRES_HOST=<your-postgres-host>
POSTGRES_PORT=<your-postgres-port>
POSTGRES_USER=<your-postgres-user>
POSTGRES_PASSWORD=<your-postgres-password>
POSTGRES_DATABASE=<your-postgres-database>

BATCH_SIZE=100000  # Optional: Customize the batch size for migration
```

#### **3. Install Dependencies (Optional for Local Use)**

If running locally (outside Docker):
```bash
pip install -r requirements.txt
```

---

### **Running the Tool**

#### **1. Using Docker**
1. **Build the Docker Image**:
   ```bash
   docker build -t db-migrator .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run --env-file .env db-migrator
   ```

3. **Optional: Enable Automatic Restarts**:
   ```bash
   docker run --env-file .env --restart=on-failure db-migrator
   ```

#### **2. Running Locally**
1. **Run the Script**:
   ```bash
   python app.py
   ```

---

### **Checkpointing**

- The script saves progress in a `migration_checkpoint.json` file in the current working directory.
- If the script crashes or is interrupted, it will automatically resume from the last checkpoint when restarted.

---

### **Customization**

- **Batch Size**: Adjust the `BATCH_SIZE` environment variable in `.env` to control the number of rows processed per batch.

---

### **Error Handling**

- **Common Issues**:
  - `relation "<table>" does not exist`: Ensure PostgreSQL credentials are correct and the database exists.
  - `Access denied for user`: Double-check the MySQL credentials and user permissions.
- Logs are printed to the console for debugging purposes.

---

### **Contributing**

Feel free to submit issues or pull requests for improvements to this tool.

---

### **Support**

If you encounter any issues, please open a GitHub issue.

