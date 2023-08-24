import re
from spacy.tokens import Span
from spacy.language import Language
from spacy.util import filter_spans
import dateparser

ordinal_to_number = {
    "first": "1", "second": "2", "third": "3", "fourth": "4", "fifth": "5",
    "sixth": "6", "seventh": "7", "eighth": "8", "ninth": "9", "tenth": "10",
    "eleventh": "11", "twelfth": "12", "thirteenth": "13", "fourteenth": "14",
    "fifteenth": "15", "sixteenth": "16", "seventeenth": "17", "eighteenth": "18",
    "nineteenth": "19", "twentieth": "20", "twenty-first": "21", "twenty-second": "22",
    "twenty-third": "23", "twenty-fourth": "24", "twenty-fifth": "25", "twenty-sixth": "26",
    "twenty-seventh": "27", "twenty-eighth": "28", "twenty-ninth": "29", "thirtieth": "30", 
    "thirty-first": "31"
}


@Language.component("find_dates")
def find_dates(doc):
    # Set up a date extension on the span
    Span.set_extension("date", default=None, force=True)

    # Ordinals
    ordinals = [
        "first", "second", "third", "fourth", "fifth",
        "sixth", "seventh", "eighth", "ninth", "tenth",
        "eleventh", "twelfth", "thirteenth", "fourteenth",
        "fifteenth", "sixteenth", "seventeenth", "eighteenth",
        "nineteenth", "twentieth", "twenty-first", "twenty-second",
        "twenty-third", "twenty-fourth", "twenty-fifth", "twenty-sixth",
        "twenty-seventh", "twenty-eighth", "twenty-ninth", "thirtieth", "thirty-first"
    ]
    
    ordinal_pattern = r"\b(?:" + "|".join(ordinals) + r")\b"

    # A regex pattern to capture a variety of date formats
    date_pattern = r"""
        # Day-Month-Year
        (?:
            \d{1,2}(?:st|nd|rd|th)?     # Day with optional st, nd, rd, th suffix
            \s+
            (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* # Month name
            (?:                         # Year is optional
                \s+
                \d{4}                   # Year
            )?
        )
        |
        # Day/Month/Year
        (?:
            \d{1,2}                     # Day
            [/-]
            \d{1,2}                     # Month
            (?:                         # Year is optional
                [/-]
                \d{2,4}                 # Year
            )?
        )
        |
        # Year-Month-Day
        (?:
            \d{4}                       # Year
            [-/]
            \d{1,2}                     # Month
            [-/]
            \d{1,2}                     # Day
        )
        |
        # Month-Day-Year
        (?:
            (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* # Month name
            \s+
            \d{1,2}(?:st|nd|rd|th)?     # Day with optional st, nd, rd, th suffix
            (?:                         # Year is optional
                ,?
                \s+
                \d{4}                   # Year
            )?
        )
        |
        # Month-Year
        (?:
            (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* # Month name
            \s+
            \d{4}                       # Year
        )
        |
        # Ordinal-Day-Month-Year
        (?:
            """ + ordinal_pattern + """
            \s+
            (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* # Month name
            (?:                         # Year is optional
                \s+
                \d{4}                   # Year
            )?
        )
        |
        (?:
            """ + ordinal_pattern + """
            \s+
            of
            \s+
            (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*  # Month name
            (?:                         # Year is optional
                \s+
                \d{4}                   # Year
            )?
        )
        |
        # Month Ordinal
        (?:
            (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*  # Month name
            \s+
            """ + ordinal_pattern + """
            (?:                         # Year is optional
                \s+
                \d{4}                   # Year
            )?
        )
    """
    matches = list(re.finditer(date_pattern, doc.text, re.VERBOSE))
    new_ents = []
    for match in matches:
        start_char, end_char = match.span()
        # Convert character offsets to token offsets
        start_token = None
        end_token = None
        for token in doc:
            if token.idx == start_char:
                start_token = token.i
            if token.idx + len(token.text) == end_char:
                end_token = token.i
        if start_token is not None and end_token is not None:
            hit_text = doc.text[start_char:end_char]
            parsed_date = dateparser.parse(hit_text)
            if parsed_date:  # Ensure the matched string is a valid date
                ent = Span(doc, start_token, end_token + 1, label="DATE")
                ent._.date = parsed_date
                new_ents.append(ent)
            else:
                # Replace each ordinal in hit_text with its numeric representation
                for ordinal, number in ordinal_to_number.items():
                    hit_text = hit_text.replace(ordinal, number)

                # Remove the word "of" from hit_text
                new_date = hit_text.replace(" of ", " ")

                parsed_date = dateparser.parse(new_date)
                ent = Span(doc, start_token, end_token + 1, label="DATE")
                ent._.date = parsed_date
                new_ents.append(ent)
    # Combine the new entities with existing entities, ensuring no overlap
    doc.ents = list(doc.ents) + new_ents
    
    return doc
