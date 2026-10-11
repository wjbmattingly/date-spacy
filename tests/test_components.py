"""Regression coverage for spoken ordinal date parsing."""

from datetime import datetime

import pytest
import spacy

import date_spacy


ORDINALS = (
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth",
    "ninth", "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth",
    "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth",
    "twenty-first", "twenty-second", "twenty-third", "twenty-fourth", "twenty-fifth",
    "twenty-sixth", "twenty-seventh", "twenty-eighth", "twenty-ninth", "thirtieth",
    "thirty-first",
)


@pytest.fixture(scope="module")
def nlp():
    pipeline = spacy.blank("en")
    pipeline.add_pipe("find_dates")
    return pipeline


@pytest.mark.parametrize("number,ordinal", list(enumerate(ORDINALS, start=1)))
@pytest.mark.parametrize("template", ["{} January 2023", "{} of January 2023", "January {} 2023"])
def test_spoken_ordinals(nlp, ordinal, number, template):
    text = template.format(ordinal)
    doc = nlp(text)
    assert [(ent.text, ent.label_, ent._.date) for ent in doc.ents] == [
        (text, "DATE", datetime(2023, 1, int(number)))
    ]


@pytest.mark.parametrize("text", [
    "thirty-first of February 2023",
    "February thirtieth 2023",
    "31 February 2023",
    "29 February 2023",
])
def test_invalid_dates_are_not_entities(nlp, text):
    assert not nlp(text).ents


@pytest.mark.parametrize("text,expected", [
    ("25th August 2023", datetime(2023, 8, 25)),
    ("January fourth 2023", datetime(2023, 1, 4)),
    ("2023-08-25", datetime(2023, 8, 25)),
    ("twenty-ninth of February 2024", datetime(2024, 2, 29)),
])
def test_existing_date_formats(nlp, text, expected):
    assert nlp(text).ents[0]._.date == expected
