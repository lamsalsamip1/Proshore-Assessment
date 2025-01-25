## RAG Agent Based Chatbot to ask queries and make bookings.

Deployed URL: https://travelbotsamip-hqa0auepdvhxduhb.canadacentral-01.azurewebsites.net/

Steps to run the chatbot locally:

1. Create a virtual environment
   `python -m venv env`
2. Install the dependencies.
   `pip install -r requirements.txt`
3. Recreate the vector database.
   ` python -m create_db.py`
4. Run the streamlit app.
   ` streamlit run app.py`

Bookings are stored in remote database
