import csv
import json
from rdflib import Graph, RDF, RDFS, OWL


def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def csv_to_text(path):
    rows = []

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            time = row.get("Time", "").strip()
            sender = row.get("Sender", "").strip()
            receiver = row.get("Receiver", "").strip()
            message = row.get("Message", "").strip()

            line = f"[{time}] {sender} -> {receiver}: {message}"
            rows.append(line)

    return "\n".join(rows)


def parse_triples(raw_output):
    triples = []

    for line in raw_output.splitlines():
        line = line.strip()

        if line.count("|") != 2:
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3:
            continue

        triples.append({
            "triple": {
                "entity": parts[0],
                "attribute": parts[1],
                "value": parts[2]
            }
        })

    return triples


def extract_allowed_relations(schema_text):
    relations = set()

    for line in schema_text.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3:
            relations.add(parts[1])

    return relations


def normalize_relation(r):
    r = r.strip()

    new = ""
    for c in r:
        if c.isupper():
            new += "_" + c.lower()
        else:
            new += c

    return new.lstrip("_")


def filter_triples(triples, allowed_relations):
    filtered = []

    normalized_allowed = {normalize_relation(r) for r in allowed_relations}

    for triple in triples:
        attr = normalize_relation(triple["triple"]["attribute"])

        if attr in normalized_allowed:
            triple["triple"]["attribute"] = attr
            filtered.append(triple)

    return filtered


def short(uri):
    uri = str(uri)
    if "#" in uri:
        return uri.split("#")[-1]
    return uri.split("/")[-1]


def ttl_to_metapaths(path):
    g = Graph()
    g.parse(path, format="turtle")

    rows = []

    # Object properties
    for prop in g.subjects(RDF.type, OWL.ObjectProperty):
        domain = g.value(prop, RDFS.domain)
        range_ = g.value(prop, RDFS.range)

        if domain and range_:
            rows.append(f"{short(domain)} | {short(prop)} | {short(range_)}")

    # Datatype properties
    for prop in g.subjects(RDF.type, OWL.DatatypeProperty):
        domain = g.value(prop, RDFS.domain)
        range_ = g.value(prop, RDFS.range)

        if domain and range_:
            rows.append(f"{short(domain)} | {short(prop)} | {short(range_)}")

    return "\n".join(rows)