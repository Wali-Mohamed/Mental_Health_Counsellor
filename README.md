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

## Interface
We use streamlit for serving the application as an API.


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

* Hit rate: 73%
* MRR: 55%
  
The improved version (with tuned boosting):

* Hit rate: 95%
* MRR: 73%

The best boosting parameters:

```bash
 boost = {
   
    'Questions': 0.20303988721391708,
    'Answers': 1.5766410134276012
    
    
    }
```


I also experimented with **lancedb semantic vector** search and got the following metrics:

* Hit rate: 95%
* MRR: 76%

##### Semantic vector search with Elasticsearch using **question_vector** and got the following metrics:
**Question Vector**
* Hit rate: 71%
* MRR: 52%
  
##### Semantic vector search with Elasticsearch using **answer_vector** and got the following metrics:
**Answer Vector**
* Hit rate: 89%
* MRR: 76%

##### Semantic vector search with Elasticsearch using **question_answer_vector** and got the following metrics:
search using
**Question Answer Vector**

* Hit rate: 87%
* MRR: 72%



  
## RAG Flow Evaluation using minsearch

We evaluated the quality of our RAG (Retrieval-Augmented Generation) flow using the LLM-as-a-Judge metric.

### Results

For **gpt-4o-mini**, in a sample of 200 records, the relevance distribution was as follows:

- **182 (91%)** RELEVANT
- **12 (6%)** PARTLY_RELEVANT
- **6 (3%)** NON_RELEVANT

We also tested **gpt-4o**, yielding:

- **190 (95%)** RELEVANT
- **5 (2.5%)** PARTLY_RELEVANT
- **5 (2.5%)** NON_RELEVANT

## RAG Flow Evaluation using lancedb vector search
For **gpt-4o-mini**, in a sample of 200 records, the relevance distribution was as follows:

- **195 (97.5%)** RELEVANT
- **3 (1.5%)** PARTLY_RELEVANT
- **2 (1%)** NON_RELEVANT


### Conclusion

The differences between the two models were minimal. Based on this, we opted to use **gpt-4o-mini** for the RAG flow.

## Monitoring
We use Grafana for monitoring the application.

It's accessible at localhost:3000:
- username: admin
- password: admin

## Monitoring Dashboard

The monitoring dashboard includes several panels to provide insights into the performance, user interaction, and cost associated with the mental health assistant:

- **Last 5 Conversations (Table):**  
  Displays a table with the five most recent conversations, detailing each question, answer, relevance, and timestamp. This panel is useful for monitoring recent user interactions.

- **+1/-1 (Pie Chart):**  
  A pie chart visualizing user feedback, with counts of positive (thumbs up) and negative (thumbs down) responses. This panel helps track user satisfaction levels.

- **Relevancy (Gauge):**  
  A gauge chart representing the relevance of responses in recent conversations. The chart uses color-coded thresholds to indicate different levels of response quality.

- **OpenAI Cost (Time Series):**  
  A time series line chart showing the cost associated with OpenAI usage over time. This panel is essential for monitoring and analyzing expenditures linked to the AI model's usage.

- **Tokens (Time Series):**  
  A time series chart tracking the number of tokens used over time. This helps to understand usage patterns and the volume of data processed in conversations.

- **Response Time (Time Series):**  
  A time series chart indicating conversation response times over time. This panel is valuable for identifying potential performance issues and ensuring the system's responsiveness.

## Acknowledgements
I thank the course trainer, Alexey Grigorev, for all his time and dedication and positive feedback as well as the course sponsors for making it possible to run this course for free.
I also thank all my colleagues for all the discussion and support in the slack channel.
