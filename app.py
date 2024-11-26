import os
import pymysql
import psycopg2
from psycopg2.extras import execute_values
import json
import requests

# Batch size for data migration
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 100000))

# Checkpoint file to track progress
CHECKPOINT_FILE = "migration_checkpoint.json"


def load_checkpoint():
    """
    Load the checkpoint file if it exists, otherwise return an empty dictionary.
    """
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as file:
            return json.load(file)
    return {}


def save_checkpoint(checkpoint):
    """
    Save the checkpoint to the checkpoint file.
    """
    with open(CHECKPOINT_FILE, "w") as file:
        json.dump(checkpoint, file)


def create_table_if_not_exists(mysql_cursor, postgres_cursor, postgres_conn, table):
    """
    Dynamically create a PostgreSQL table based on the schema of the MySQL table.
    """
    # Get schema from MySQL
    mysql_cursor.execute(f"DESCRIBE {table};")
    columns = mysql_cursor.fetchall()

    # Build CREATE TABLE statement for PostgreSQL
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table} ("
    column_definitions = []

    for column in columns:
        col_name = column[0]
        col_type = column[1]

        # Map MySQL data types to PostgreSQL data types
        if "int" in col_type:
            pg_type = "INTEGER"
        elif "varchar" in col_type or "text" in col_type:
            pg_type = "TEXT"
        elif "datetime" in col_type:
            pg_type = "TIMESTAMP"
        elif "float" in col_type or "double" in col_type:
            pg_type = "DOUBLE PRECISION"
        elif "decimal" in col_type:
            pg_type = "NUMERIC"
        else:
            pg_type = "TEXT"  # Default fallback

        # Add column definition
        nullable = "NOT NULL" if column[2] == "NO" else ""
        column_definitions.append(f"{col_name} {pg_type} {nullable}")

    create_table_query += ", ".join(column_definitions) + ");"

    # Execute CREATE TABLE query
    postgres_cursor.execute(create_table_query)
    postgres_conn.commit()
    print(f"Table {table} created or already exists in PostgreSQL.")


def send_notification(message):
    """
    Sends a message to a Discord webhook.

    Parameters:
        message (str): The message to send.

    Returns:
        bool: True if the message is successfully sent, False otherwise.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    data = {
        "content": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(webhook_url, json=data, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        return False

def migrate_data():
    """
    Migrate data from MySQL to PostgreSQL with table creation automation and resumption support.
    """
    checkpoint = load_checkpoint()

    try:
        # Connect to MySQL and PostgreSQL
        mysql_conn = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            charset="utf8mb4",
        )
        mysql_cursor = mysql_conn.cursor()

        postgres_conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=int(os.getenv("POSTGRES_PORT")),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DATABASE"),
            options="-c search_path=public",
        )
        postgres_cursor = postgres_conn.cursor()

        # Fetch all tables from MySQL
        mysql_cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in mysql_cursor.fetchall()]

        for table in tables:
            print(f"Migrating table: {table}")

            # Ensure the table exists in PostgreSQL
            create_table_if_not_exists(mysql_cursor, postgres_cursor, postgres_conn, table)

            # Get total rows in the MySQL table
            mysql_cursor.execute(f"SELECT COUNT(*) FROM {table};")
            total_rows = mysql_cursor.fetchone()[0]
            print(f"Total rows to migrate: {total_rows}")

            # Resume from last checkpoint
            offset = checkpoint.get(table, 0)

            # Migrate data in batches
            while offset < total_rows:
                mysql_cursor.execute(f"SELECT * FROM {table} LIMIT {BATCH_SIZE} OFFSET {offset};")
                rows = mysql_cursor.fetchall()

                if rows:
                    # Insert rows into PostgreSQL
                    insert_query = f"INSERT INTO {table} VALUES %s"
                    execute_values(postgres_cursor, insert_query, rows)
                    print(f"Migrated {offset + len(rows)}/{total_rows} rows")

                offset += len(rows)
                postgres_conn.commit()

                # Update and save checkpoint
                checkpoint[table] = offset
                save_checkpoint(checkpoint)

        print("Migration complete!")
        send_notification("Data migration complete!")

    except Exception as e:
        print("Error:", e)
    finally:
        # Close database connections
        mysql_cursor.close()
        mysql_conn.close()
        postgres_cursor.close()
        postgres_conn.close()


if __name__ == "__main__":
    migrate_data()
