import sqlite3

# Create a connection

connection=sqlite3.connect("student.db")

# Create a cursor object to create a record

cursor=connection.cursor()

# Create the table

table_info = """
CREATE TABLE STUDENT (
    NAME VARCHAR(25),
    CLASS VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS INT
)
"""
cursor.execute(table_info)

# iNSERT 

cursor.execute('''Insert into STUDENT values('Anshika','DataScience','A',90)''')
cursor.execute('''Insert into STUDENT values('Utkarsh','Computer','B',90)''')
cursor.execute('''Insert into STUDENT values('Mukesh','Computer','B',99)''')
cursor.execute('''Insert into STUDENT values('Neelam','Hindi','B',79)''')
cursor.execute('''Insert into STUDENT values('Maneesh','Social Science','B',79)''')


# Display all records

print("The inserted records are")
data=cursor.execute('''Select * from STUDENT''')
for row in data:
  print(row)


# Commit your changes in DB
connection.commit()
connection.close()