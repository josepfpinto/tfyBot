from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY)
conversation = ConversationChain(
    llm=llm, memory=ConversationBufferWindowMemory(k=4), verbose=True)
