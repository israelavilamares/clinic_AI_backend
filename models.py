# models.py
from database import Base, engine, metadata

# Reflejar las tablas de la base de datos
def reflect_tables():
    metadata.reflect(bind=engine)  # Esto obtiene todas las tablas de la base de datos
    for table_name, table in metadata.tables.items():
        # Crea un modelo de SQLAlchemy para cada tabla reflejada
        print(f"Reflejando tabla: {table_name}")
        globals()[table_name] = type(table_name, (Base,), {
            '__tablename__': table_name,
            '__table__': table
        })

# Llamar a la función de reflección
reflect_tables()
