import pandas as pd
from sqlalchemy import create_engine, text, exc
from sqlalchemy.exc import SQLAlchemyError  # Added this import
import logging
import os
from typing import Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "jhorshuar"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "pyrolysis_db"),
    "admin_db": "postgres"
}

def create_database_if_not_exists(config: dict) -> None:
    """Create the database if it doesn't exist."""
    admin_conn_string = (
        f"postgresql+psycopg2://{config['user']}:{config['password']}@"
        f"{config['host']}:{config['port']}/{config['admin_db']}"
    )
    
    try:
        admin_engine = create_engine(admin_conn_string, isolation_level="AUTOCOMMIT")
        with admin_engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": config["database"]}
            )
            
            if not result.scalar():
                logger.info(f"Creating database {config['database']}")
                conn.execute(text(f"CREATE DATABASE {config['database']}"))
                logger.info(f"Database {config['database']} created successfully")
            else:
                logger.info(f"Database {config['database']} already exists")
                
    except exc.OperationalError as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        if "password authentication failed" in str(e):
            logger.error("Please verify your PostgreSQL username and password")
        raise
    finally:
        if 'admin_engine' in locals():
            admin_engine.dispose()

def create_db_engine(config: dict) -> create_engine:
    """Create and return a database engine."""
    try:
        connection_string = (
            f"postgresql+psycopg2://{config['user']}:{config['password']}@"
            f"{config['host']}:{config['port']}/{config['database']}"
        )
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        logger.info("Database engine created and connection verified")
        return engine
        
    except exc.OperationalError as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        if "does not exist" in str(e):
            logger.error(f"Database {config['database']} doesn't exist - trying to create it")
            create_database_if_not_exists(config)
            return create_db_engine(config)
        raise
    except Exception as e:
        logger.error(f"Error creating database engine: {str(e)}")
        raise

def load_csv_files() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load and validate CSV files."""
    try:
        feed = pd.read_csv("../data/plastic_feedstock.csv")
        blend = pd.read_csv("../data/blend_compositions.csv")
        condition = pd.read_csv("../data/pyrolysis_conditions.csv")
        output = pd.read_csv("../data/pyrolysis_outputs.csv")
        
        # Data validation - ensure char_yield is non-negative
        output['char_yield'] = output['char_yield'].clip(lower=0)  # Fix negative values
        
        for df, name in zip([feed, blend, condition, output], 
                          ["feedstock", "blend", "conditions", "outputs"]):
            if df.empty:
                raise ValueError(f"{name} DataFrame is empty")
        
        logger.info("CSV files loaded and validated successfully")
        return feed, blend, condition, output
        
    except FileNotFoundError as e:
        logger.error(f"CSV file not found: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error loading CSV files: {str(e)}")
        raise

def setup_database_schema(engine: create_engine) -> None:
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
        percentage FLOAT CHECK (percentage > 0 AND percentage <= 100),
        CONSTRAINT unique_blend_composition UNIQUE (blend_id, plastic_id)
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

def load_data_to_db(
    engine: create_engine,
    feed: pd.DataFrame,
    blend: pd.DataFrame,
    condition: pd.DataFrame,
    output: pd.DataFrame
) -> None:
    """Load data into database tables with error handling."""
    try:
        with engine.begin() as conn:
            feed.to_sql(
                "plastic_feedstock", 
                con=conn, 
                if_exists="append", 
                index=False,
                chunksize=1000
            )
            blend.to_sql(
                "blend_compositions", 
                con=conn, 
                if_exists="append", 
                index=False,
                chunksize=1000
            )
            condition.to_sql(
                "pyrolysis_conditions", 
                con=conn, 
                if_exists="append", 
                index=False,
                chunksize=1000
            )
            output.to_sql(
                "pyrolysis_outputs", 
                con=conn, 
                if_exists="append", 
                index=False,
                chunksize=1000
            )
        logger.info("Data loaded to database successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error loading data to database: {str(e)}")
        raise

def main() -> bool:
    """Main execution function."""
    try:
        logger.info("Starting database setup process")
        
        engine = create_db_engine(DB_CONFIG)
        feed, blend, condition, output = load_csv_files()
        setup_database_schema(engine)
        load_data_to_db(engine, feed, blend, condition, output)
        
        logger.info("Database setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Application failed: {str(e)}", exc_info=True)
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("Database Setup Script")
    print("---------------------")
    
    try:
        create_database_if_not_exists(DB_CONFIG)
    except Exception as e:
        print(f"\nFATAL: Could not initialize database: {str(e)}")
        print("Please ensure:")
        print("1. PostgreSQL is running")
        print("2. Your credentials in DB_CONFIG are correct")
        print("3. You have privileges to create databases")
        exit(1)
    
    if success := main():
        print("\nSUCCESS: Database setup completed")
    else:
        print("\nERROR: Database setup failed - check logs for details")