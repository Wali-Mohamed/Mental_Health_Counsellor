# Mental Health Assistant

![Alt text](./App/images/mental_health.jpg)

### Problem Statement

Mental health is an essential aspect of overall well-being, impacting emotional, psychological, and social aspects of life. It affects how individuals think, feel, and behave, as well as their ability to handle stress, form relationships, and make decisions. Despite its importance, mental health issues are widespread, and navigating reliable information on mental health can be challenging.

To address this, our project aims to provide accessible, reliable answers to frequently asked questions (FAQs) about mental health. Using a large language model (LLM) trained on a dataset compiled from trusted sources, this project delivers insights into common mental health questions, helping users understand and manage their mental well-being effectively.

This project leverages data from sources such as:
- [The Kim Foundation](https://www.thekimfoundation.org/faqs/)
- [Mental Health America](https://www.mhanational.org/frequently-asked-questions)
- [Wellness in Mind](https://www.wellnessinmind.org/frequently-asked-questions/)
- [Here to Help BC](https://www.heretohelp.bc.ca/questions-and-answers)

Our goal is to make mental health information more accessible and improve awareness, ultimately supporting better mental health outcomes.
## Dataset
The dataset is structured as follows, with each entry containing a unique identifier, a mental health-related question, and its corresponding answer:

```json
{
    "Question_ID": 1590140,
    "Questions": "What does it mean to have a mental illness?",
    "Answers": "Mental illnesses are health conditions that disrupt a person’s thoughts, emotions, relationships, and daily functioning. They are associated with distress and diminished capacity to engage in the ordinary activities of daily life.\nMental illnesses fall along a continuum of severity: some are fairly mild and only interfere with some aspects of life, such as certain phobias. On the other end of the spectrum lie serious mental illnesses, which result in major functional impairment and interference with daily life."
}

```

Each row in this dataset includes:

- Question_ID: A unique identifier for each question.
- Questions: The mental health-related question posed by users.
- Answers: The answer associated with the question, designed to provide helpful and informative responses based on reputable mental health resources.

## Technologies

The project leverages several key technologies to build, deploy, and monitor the mental health assistant:

- **Streamlit**: Provides an interactive front-end, allowing users to input mental health-related questions and view responses in a user-friendly interface.
  
- **Docker & Docker Compose**: Used to containerize the application, ensuring consistency across different environments and simplifying dependency management.
  
- **PostgreSQL**: Acts as the database to store conversations, user feedback, and various usage statistics.

- **OpenAI API**: Utilized for generating answers to mental health-related queries by leveraging large language models (LLMs).

- **Grafana**: Employed for monitoring and visualizing application performance, enabling tracking of metrics such as response time and token usage.

- **Elasticsearch**: Provides a text search engine to support efficient and scalable querying of user inputs, enhancing the assistant’s ability to retrieve relevant information.

- **LanceDB**: Used as a vector database for storing and managing embeddings, facilitating semantic search and similarity-based retrieval.

- **MinSearch**: A tool for lightweight full-text search, enabling fast and efficient searches within the dataset.

- **Pandas**: A Python library for data manipulation and analysis, helping process and transform data during setup and analysis stages.

- **Python Libraries**:
  - `psycopg2`: Manages database connections with PostgreSQL, enabling efficient data storage and retrieval.
  - `dotenv`: Loads environment variables from .env files, simplifying configuration management.
  - `base64` and `uuid`: Used for encoding data and generating unique IDs.


## Preparation
### Clone Repository

```bash
git clone https://github.com/Wali-Mohamed/Mental_Health_Counsellor
cd app
```


Before running the application, ensure that all necessary dependencies are installed. One key dependency is `python-dotenv`, a Python package that helps load environment variables from a `.env` file into the application.

1. **Install python-dotenv**:
   ```bash
   pip install python-dotenv
   ```

 #### Running it locally with dockerizing  

Install dependencies
```bash
pip install -r requirements.txt

```
Then to app directory and run db_prep.py for database preparation

```bash
cd app
export POSTGRES_HOST=localhost
python db_prep.py

```
To check the content of the database, use pgcli (already installed with pipenv):
```bash
pgcli -h localhost -U your_username -d mental_health -W

```
You will asked for a password
Please type in your database password

You can view the schema using the \d command:

```bash
\d conversations;
```

And select from this table:
```bash
select * from conversations;
```

To run the app, run the following code.

```bash
streamlit run app.py

```


### Running the application with containerization

To install dependencies, build images and run them

Change to the app directory
```bash
cd app
```
Build the images for app, postgres database and grafana.
```bash
docker-compose up --build
```
#### Initialize the Database:

- Ensure Docker is running on your machine.
- Start only the PostgreSQL container to set up the database:

```bash
docker-compose up -d postgres
```

- Run the db_prep.py script to initialize tables and seed data:

```bash
docker-compose exec app python db_prep.py
```
That will create the two tables: conversations and feedback

##### Run the Application:

- Start all services with Docker Compose:
```bash
docker-compose up --build

```
The application should now be accessible at http://localhost:8501



### Code
The code for the application is in the app folder:

- app.py - the Flask API, the main entrypoint to the application
- rag.py - the main RAG logic for building the retrieving the data and building the prompt
- ingest.py - loading the data into the knowledge base
- minsearch.py - an in-memory search engine
- db.py - the logic for logging the requests and responses to postgres
- db_prep.py - the script for initializing the database

We also have some code in the project root directory:

## Experiments
For experiments, we use Jupyter notebooks. They are in the notebooks folder.

To start Jupyter, run:
```bash
cd notebooks
jupyter notebook
```
We have the following notebooks:

- 1-RAG-test.ipynb: The RAG flow and evaluating the system.
- 2-RAG-test_with_Vector_Search.ipynb: The RAG flow and evaluating the system.
- 3-groundtruth-data_generation.ipynb: Generating the ground truth dataset for retrieval evaluation.
- Retrieval evaluation

The basic approach - using minsearch without any boosting - gave the following metrics:

Hit rate: 94%
MRR: 82%
The improved version (with tuned boosting):

Hit rate: 94%
MRR: 90%
The best boosting parameters:

boost = {
    'exercise_name': 2.11,
    'type_of_activity': 1.46,
    'type_of_equipment': 0.65,
    'body_part': 2.65,
    'type': 1.31,
    'muscle_groups_activated': 2.54,
    'instructions': 0.74
}
