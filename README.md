Certainly! Here's a README for your `date_spacy` package:

---

# Date spaCy

![date spacy logo](images/date_spacy_logo.png)

Date spaCy is a collection of custom spaCy pipeline component that enables you to easily identify date entities in a text and fetch the parsed date values using spaCy's token extensions. It uses RegEx to find dates and then uses the [dateparser](https://dateparser.readthedocs.io/en/latest/) library to convert those dates into structured datetime data. One current limitation is that if no year is given, it presumes it is the current year. The `dateparser` output is stored in a custom entity extension: `._.date`.

This lightweight approach can be added to an existing spaCy pipeline or to a blank model. If using in an existing spaCy pipeline, be sure to add it before the NER model.

## Installation

To install `date_spacy`, simply run:

```bash
pip install date-spacy
```

## Usage

### Adding the Component to your spaCy Pipeline

First, you'll need to import the `find_dates` component and add it to your spaCy pipeline:

```python
import spacy
from date_spacy import find_dates

# Load your desired spaCy model
nlp = spacy.blank('en')

# Add the component to the pipeline
nlp.add_pipe('find_dates')
```

### Processing Text with the Pipeline

After adding the component, you can process text as usual:

```python
doc = nlp("The event is scheduled for 25th August 2023.")
```

### Accessing the Parsed Dates

You can iterate over the entities in the `doc` and access the special date extension:

```python
for ent in doc.ents:
    if ent.label_ == "DATE":
        print(f"Text: {ent.text} -> Parsed Date: {ent._.date}")
```

This will output:

```
Text: 25th August 2023 -> Parsed Date: 2023-08-25 00:00:00
```