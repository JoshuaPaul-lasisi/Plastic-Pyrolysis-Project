import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration (use environment variables or config file in production)
DB_CONFIG = {
    "user": "postgres",  # Corrected from "postgre"
    "password": "jhorshuar",
    "host": "localhost",
    "port": "5432",
    "database": "pyrolysis_db"
}

def create_db_engine(config):
    """Create and return a database engine with error handling."""
    try:
        connection_string = (
            f"postgresql+psycopg2://{config['user']}:{config['password']}@"
            f"{config['host']}:{config['port']}/{config['database']}"
        )
        engine = create_engine(connection_string)
        logger.info("Database engine created successfully")
        return engine
    except Exception as e:
        logger.error(f"Error creating database engine: {str(e)}")
        raise

def load_csv_files():
    """Load CSV files with error handling."""
    try:
        feed = pd.read_csv("data/plastic_feedstock_large.csv")
        blend = pd.read_csv("data/blend_compositions_large.csv")
        condition = pd.read_csv("data/pyrolysis_conditions_large.csv")
        output = pd.read_csv("data/pyrolysis_outputs_large.csv")
        logger.info("CSV files loaded successfully")
        return feed, blend, condition, output
    except FileNotFoundError as e:
        logger.error(f"CSV file not found: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error loading CSV files: {str(e)}")
        raise

def setup_database_schema(engine):
    """Create database schema with proper error handling."""
    schema_sql = """
    DROP TABLE IF EXISTS pyrolysis_outputs, pyrolysis_conditions, 
                 blend_compositions, plastic_feedstock CASCADE;

    CREATE TABLE plastic_feedstock (
        plastic_id TEXT PRIMARY KEY,
        plastic_type TEXT NOT NULL,
        density FLOAT CHECK (density > 0),
        melting_point INT CHECK (melting_point > 0),
        degradation_temp INT CHECK (degradation_temp > 0),
        additives_present TEXT
    );

    CREATE TABLE blend_compositions (
        id SERIAL PRIMARY KEY,
        blend_id TEXT NOT NULL,
        plastic_id TEXT NOT NULL REFERENCES plastic_feedstock(plastic_id),
        percentage FLOAT CHECK (percentage > 0 AND percentage <= 100)
    );

    CREATE TABLE pyrolysis_conditions (
        condition_id TEXT PRIMARY KEY,
        blend_id TEXT,
        temperature INT CHECK (temperature > 0),
        heating_rate FLOAT CHECK (heating_rate > 0),
        residence_time INT CHECK (residence_time > 0),
        catalyst TEXT,
        reactor_type TEXT,
        energy_input FLOAT CHECK (energy_input > 0)
    );

    CREATE TABLE pyrolysis_outputs (
        output_id TEXT PRIMARY KEY,
        condition_id TEXT NOT NULL REFERENCES pyrolysis_conditions(condition_id),
        fuel_yield FLOAT CHECK (fuel_yield >= 0 AND fuel_yield <= 100),
        gas_yield FLOAT CHECK (gas_yield >= 0 AND gas_yield <= 100),
        char_yield FLOAT CHECK (char_yield >= 0 AND char_yield <= 100),
        fuel_energy_content FLOAT CHECK (fuel_energy_content > 0),
        emissions FLOAT CHECK (emissions >= 0),
        efficiency FLOAT CHECK (efficiency >= 0)
    );
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(schema_sql))
            conn.commit()
        logger.info("Database schema created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database schema: {str(e)}")
        raise

def load_data_to_db(engine, feed, blend, condition, output):
    """Load data into database tables with error handling."""
    try:
        with engine.begin() as conn:  # Automatically commits or rolls back
            feed.to_sql(
                "plastic_feedstock", 
                con=conn, 
                if_exists="append", 
                index=False
            )
            blend.to_sql(
                "blend_compositions", 
                con=conn, 
                if_exists="append", 
                index=False
            )
            condition.to_sql(
                "pyrolysis_conditions", 
                con=conn, 
                if_exists="append", 
                index=False
            )
            output.to_sql(
                "pyrolysis_outputs", 
                con=conn, 
                if_exists="append", 
                index=False
            )
        logger.info("Data loaded to database successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error loading data to database: {str(e)}")
        raise

def main():
    try:
        # Initialize database connection
        engine = create_db_engine(DB_CONFIG)
        
        # Load CSV data
        feed, blend, condition, output = load_csv_files()
        
        # Setup database schema
        setup_database_schema(engine)
        
        # Load data into database
        load_data_to_db(engine, feed, blend, condition, output)
        
        logger.info("Database setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("Database tables created and data loaded successfully.")
    else:
        print("Database setup failed. Check logs for details.")