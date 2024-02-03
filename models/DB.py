import psycopg2
import psycopg2.extras

class DB:
    def __init__(self, **kwargs):
        self._conn = psycopg2.connect(**kwargs)
  
    """
        performa o comando select e retorna a tabela

        cmd : str
            comando sql com o select
    """

    def select(self, cmd):
        with self._conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cur:
            cur.execute(cmd)
            records = cur.fetchall()
        return records

    """
        performa o comando insert

        table_name : str
            nome da tabela

        columns : [str]
            nomes das colunas que serão usadas para inserir

        values : [str]
            valores que serão inseridos nas colunas na mesma ordem de "columns" 
            
    """

    def insert(self, table_name, columns, values):
        with self._conn.cursor() as cur:
            comma_columns = ','.join(columns)
            comma_values = ','.join([str(val) for val in values])
            cur.execute(f"INSERT INTO {table_name} (comma_columns) VALUES ({comma_values})")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self._conn.close()

    
