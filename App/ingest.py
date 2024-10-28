import os
import pandas as pd
import minsearch


data_path = './data/Mental_Health_FAQ.csv'  



def load_index(data_path=data_path):
    df = pd.read_csv(data_path)
    
    documents = df.to_dict(orient="records")

    index = minsearch.Index(
        text_fields=[
            
            "Questions",
            "Answers"
        ],
        keyword_fields=["Question_ID"],
    )

    index.fit(documents)
    return index