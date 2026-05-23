import psycopg2
import pandas as pd
from sshtunnel import SSHTunnelForwarder
from config.settings import (
    DB_HOST,
    DB_PASSWORD,
    DB_NAME,
    DB_PORT,
    DB_USER,
    SSH_IP,
    SSH_PRIVATE_KEY,
    SSH_USERNAME,
    SSH_PORT,
    DATA_DIR
)


class DatabaseConnection:
    def __init__(self, *,
                 DB_HOST,
                 DB_PASSWORD,
                 DB_NAME,
                 DB_PORT,
                 DB_USER,
                 SSH_IP,
                 SSH_PRIVATE_KEY,
                 SSH_USERNAME,
                 SSH_PORT
                 ):
        self.db_host = DB_HOST
        self.db_password = DB_PASSWORD
        self.db_name = DB_NAME
        self.db_port = int(DB_PORT)
        self.db_user = DB_USER
        self.ssh_ip = SSH_IP
        self.ssh_username = SSH_USERNAME
        self.ssh_private_key = SSH_PRIVATE_KEY
        self.ssh_port = int(SSH_PORT)
        """
        Initializes the database connection configuration and SSH tunnel credentials.

        Parameters
        ----------
        DB_HOST : str
            The host address or endpoint of the remote database server.
        DB_PASSWORD : str
            The password used to authenticate the database user.
        DB_NAME : str
            The name of the specific database to connect to.
        DB_PORT : int or str
            The port number where the database service is listening on the remote host.
        DB_USER : str
            The username used to authenticate the database connection.
        SSH_IP : str
            The public IP address or hostname of the SSH bastion/jump server.
        SSH_PRIVATE_KEY : str
            The secure private key string (or path) used for SSH key-based authentication.
        SSH_USERNAME : str
            The username used to log in to the SSH bastion server.
        SSH_PORT : int or str
            The port number where the SSH service is listening on the bastion server.
        """

    def setup_status(self):
        """
        Prints the current configuration parameters and their data types for debugging.

        Verifies that essential credentials like the database password are correctly 
        set and prints a masked placeholder for the password to maintain security.
        It also logs the data types of both database and SSH configuration variables.

        Raises
        ------
        ValueError
            If the DB_PASSWORD attribute is empty, None, or evaluated as a falsy value.
        """

        print(f'DB Host: {self.db_host} -> as {type(self.db_host)}')
        print(f'DB name: {self.db_name} -> as {type(self.db_name)}')
        if not self.db_password:
            raise ValueError('Password was not set correctly')
        else:
            print('Password: *******')
        print(f'DB port: {self.db_port} -> as {type(self.db_port)}')
        print(f'DB username: {self.db_user} -> as {type(self.db_user)}')

        print(f'ssh ip: {self.ssh_ip} -> as {type(self.ssh_ip)}')
        print(f'ssh username: {self.ssh_username} -> as {type(self.ssh_username)}')
        print(f'ssh private key: {self.ssh_private_key} -> as {type(self.ssh_private_key)}')
        print(f'ssh port: {self.ssh_port} -> as {type(self.ssh_port)}')

    def set_connection(self, *, query: str = None):
        """
        Establishes a secure SSH tunnel to execute a query or test the connection to PostgreSQL.

        Dynamically routes the database traffic through a local port forwarding setup 
        using an SSH bastion host. If a query is provided, it executes the SQL statement 
        and fetches the results; otherwise, it acts as a connection health check.

        Parameters
        ----------
        query : str, optional
            The SQL query statement to be executed on the database. If None, the method 
            only establishes and tests the connection before closing it. Default is None.

        Returns
        -------
        bool
            Returns True if query is None and the connection tests successfully.
        tuple (list of tuples, list of str)
            If a valid query is provided, returns a tuple containing:
            - res: The fetched rows from the cursor as a list of tuples.
            - headers: A list of column names extracted from the cursor description.
        None
            Returns None if an exception occurs during the SSH tunneling or database execution.
        """
        try:

            with SSHTunnelForwarder(
                (self.ssh_ip, int(self.ssh_port)),
                ssh_private_key=self.ssh_private_key,
                ssh_username=self.ssh_username,

                remote_bind_address=(self.db_host, int(self.db_port)),
                local_bind_address=('127.0.0.1',),
                host_pkey_directories=[]
                ) as server:

                print('Server connected')

                params = {
                    'database': self.db_name,
                    'user': self.db_user,
                    'password': self.db_password,
                    'host': '127.0.0.1',
                    'port': server.local_bind_port
                }

                conn = psycopg2.connect(**params)
                curs = conn.cursor()

                if query is None:
                    print("database connected")
                    curs.close()
                    conn.close()
                    return True

                else:
                    print(f'Query: {query}')
                    curs.execute(query)
                    headers = [desc[0] for desc in curs.description]

                    res = curs.fetchall()

                    curs.close()
                    conn.close()
                    return res, headers

        except Exception as e:
            print(f'Connection error. {e}')

    def query_to_csv(self, *, query: str = None, output_file_name: str = 'output.csv'):
        """
        Converts the results of an SQL query into a structured CSV file using pandas.

        Leverages the secure SSH connection method to fetch data and metadata (headers),
        builds a pandas DataFrame, displays a short preview of the data in the console,
        and exports the final dataset to a local CSV file with UTF-8 encoding.

        Parameters
        ----------
        query : str, optional
            The SQL query statement to extract data from the database. Default is None.
        output_file_name : str, optional
            The file name or destination path where the CSV file will be saved. 
            Default is 'output.csv'.

        Returns
        -------
        pd.DataFrame
            The pandas DataFrame containing the query results and headers if successfully exported.
        bool
            Returns False if no query is provided or if an exception occurs during 
            the connection, execution, or file writing process.
        """

        """
        Converts a query into a csv file.
        """        

        try:
            if not query:
                print("There is no query provided")
                return False
                
            data, headers = self.set_connection(query=query)

            df = pd.DataFrame(data, columns=headers)
            
            print("\nPreview\n")
            print(df.head())
            
            df.to_csv(output_file_name, index=False, encoding='utf-8')
            print(f"\nDF succesfully created and saved as '{output_file_name}'")
            return df
            
        except Exception as e:
            print(f"Error while exporting to CSV: {e}")
            return False


if __name__ == '__main__':
    new_conn = DatabaseConnection(
        DB_HOST=DB_HOST,
        DB_NAME=DB_NAME,
        DB_PASSWORD=DB_PASSWORD,
        DB_PORT=DB_PORT,
        DB_USER=DB_USER,
        SSH_PRIVATE_KEY=SSH_PRIVATE_KEY,
        SSH_IP=SSH_IP,
        SSH_USERNAME=SSH_USERNAME,
        SSH_PORT=SSH_PORT
        )

    new_conn.setup_status()
    new_conn.set_connection()
    #set the query to bring sales data
    sales_query = """
    SELECT * FROM sale_transactions
    """
    #fix output path
    output_path = f'{DATA_DIR}/sales.csv'


    #convert query to a csv and convert it as a df
    sales = new_conn.query_to_csv(query=sales_query, output_file_name=output_path)