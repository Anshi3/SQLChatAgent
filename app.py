import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")


LOCALDB="USE_LOCALDB"
MYSQL="USE_MYSQL"

# Create a radio button
radio_opt=["Use SQLLite 3 Database- Student.db","Connect to you MySQL Database"]

selected_output=st.sidebar.radio(label="Choose the DB which you want to chat",options=radio_opt)

if(radio_opt).index(selected_output)==1:
  db_uri=MYSQL
  mysql_host=st.sidebar.text_input("Provide MySQL Host")
  mysql_user=st.sidebar.text_input("MYSQL User")
  mysql_password=st.sidebar.text_input("MYSQL password",type="password")
  mysql_db=st.sidebar.text_input("MySQL database")
else:
  db_uri=LOCALDB

api_key=st.sidebar.text_input(label="GRoq API Key",type="password")

# Check if given correctly

if not db_uri:
    st.info("Please enter the database information and uri")

if not api_key:
    st.info("Please add the groq api key")

## LLM model
llm=ChatGroq(groq_api_key=api_key,model_name="Llama3-8b-8192",streaming=True)


# Streamlit's cache decorator to store the result for performance
@st.cache_resource(ttl="2h")  # This caches the DB connection for 2 hours (TTL = Time to Live)
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    """
    This function returns a configured SQLDatabase connection
    based on the db_uri (either LOCALDB or MYSQL).
    """

    # Case 1: If using local SQLite DB
    if db_uri == LOCALDB:
        # Get the absolute path of the SQLite database file (student.db)
        dbfilepath = (Path(__file__).parent / "student.db").absolute()

        # Print the full path of DB (for debugging purposes)
        print(dbfilepath)

        # Define a creator lambda to open the SQLite file in read-only mode using URI
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)

        # Return a SQLDatabase object using the engine with our custom creator
        return SQLDatabase(create_engine("sqlite:///", creator=creator))

    # Case 2: If using MySQL DB
    elif db_uri == MYSQL:
        # If any MySQL connection detail is missing, show error and stop execution
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()  # Stop Streamlit from running further

        # Return SQLDatabase object using MySQL URI (mysql+mysqlconnector is the driver)
        return SQLDatabase(
            create_engine(
                f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"
            )
        )


if db_uri==MYSQL:
    db=configure_db(db_uri,mysql_host,mysql_user,mysql_password,mysql_db)
else:
    db=configure_db(db_uri)


# toolkit kaise create karna h

toolkit=SQLDatabaseToolkit(db=db,llm=llm)

agent=create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

    


if "messages" not in st.session_state or st.sidebar.button("Clear mesage history"):
    st.session_state["messages"]=[{"role":"assistant","content":"How can I help you"}]

for msg in st.session_state.messages:
  st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
      streamlit_callback=StreamlitCallbackHandler(st.container())
      response=agent.run(user_query,callbacks=[streamlit_callback])
      st.session_state.messages.append({"role":"assistant","content":response})
      st.write(response)



# 🔸 User ka message session_state mein add ho jaata hai so that chat persist rahe


# 🔸 msg["role"] — yeh define karta hai ki message kisne bheja: "user" ya "assistant"
# 🔸 st.chat_message() — Streamlit ka naya chat-like bubble UI banata hai

#  st.session_state — Streamlit ka temporary memory hota hai jo browser refresh pe bhi data yaad rakhta hai
# 🔸 Pehli baar ya clear button dabane pe message list reset ho jaata hai

