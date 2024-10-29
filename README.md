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

json
Copy code
{
    "Question_ID": 1590140,
    "Questions": "What does it mean to have a mental illness?",
    "Answers": "Mental illnesses are health conditions that disrupt a person’s thoughts, emotions, relationships, and daily functioning. They are associated with distress and diminished capacity to engage in the ordinary activities of daily life.\nMental illnesses fall along a continuum of severity: some are fairly mild and only interfere with some aspects of life, such as certain phobias. On the other end of the spectrum lie serious mental illnesses, which result in major functional impairment and interference with daily life."
}
Each row in this dataset includes:

Question_ID: A unique identifier for each question.
Questions: The mental health-related question posed by users.
Answers: The answer associated with the question, designed to provide helpful and informative responses based on reputable mental health resources.
