import json
import os
from typing import Any, Dict, List, Tuple, Union
from tqdm import tqdm

def read_conll(fp: str, label_delimiter:str = "-", encoding:str='utf-8'):
    """
    Read conll-2003 BMES file
    
    Format:
    
    北 B-LOC
    京 I-LOC
    欢 O
    迎 O
    你 O

    Args:
        fp (str): The relative or absolute file path. 
        label_delimiter (str, optional): Default symbom of the delimiter. Defaults to "-".
        encoding (str, optional): The encoding of file. Defaults to "utf-8".

    Returns:
        Tuple[List,Set]: Return the sentence and the list of entity types within the boundary [l, r).
    """
    sentences = []
    entity_type_set = set()
    def init_sentence():
        return [],[]
    def init_entity():
        return {
            "start": -1,
            "end": -1,
            "entity": "",
            "text": []
        }
    sentence, entities = init_sentence()
    entity = init_entity()
    with open(fp, "r", encoding=encoding) as f:
        for line in f:
            line = line.strip().split()
            if len(line)==2 or (len(line)>0 and line[-1][0] in ("B", "M", "I", "E", "S")):
                if len(line)==2:
                    ch, label = line 
                else:
                    # case ' ' O
                    ch, label = ' ', line[-1]
                sentence.append(ch)
                if label.startswith("B") or label.startswith("S"):
                    if entity["end"]!=-1:
                        entities.append(entity)
                    entity = init_entity()
                    entity["start"] = len(sentence) - 1
                    entity["end"] = len(sentence)
                    entity["text"].append(ch)
                    entity["entity"] = label_delimiter.join(label.split(label_delimiter)[1:])
                    if label.startswith("S"):
                        entities.append(entity)
                        entity = init_entity()
                elif label.startswith("I") or label.startswith("M"):
                    if entity["start"]==-1:
                        entity["start"] = len(sentence)-1
                    entity["text"].append(ch)
                    entity["end"] = len(sentence)
                    if entity["entity"]=="":
                        entity["entity"] = label_delimiter.join(label.split(label_delimiter)[1:])
                elif label.startswith("E"):
                    if entity["start"]==-1:
                        entity["start"] = len(sentence)-1
                    entity["text"].append(ch)
                    entity["end"] = len(sentence)
                    if entity["entity"]=="":
                        entity["entity"] = label_delimiter.join(label.split(label_delimiter)[1:])
                    entities.append(entity)
                    entity = init_entity()
                elif label.startswith("O"):
                    if entity["end"]!=-1:
                        entities.append(entity)
                        entity = init_entity()
                else:
                    raise NotImplementedError()
            else:
                # next sentence
                if len(sentence)>0:
                    sentences.append({
                        "text": sentence,
                        "entities": entities
                    })
                    # fix: variable "entity" leak
                    for _entity in entities:
                        entity_type_set.add(_entity["entity"])
                entity = init_entity()
                sentence, entities = init_sentence()
        # last entity
        if entity["end"]!=-1:
            entities.append(entity)
        if len(sentence)>0:
            sentences.append({
                "text": sentence,
                "entities": entities
            })
            # fix: variable "entity" leak
            for _entity in entities:
                entity_type_set.add(_entity["entity"])
    return sentences, list(sorted(entity_type_set))

def read_weibo(fp:str, label_delimiter:str = "-", encoding:str='utf-8'):
    """
    Read original weibo dataset.
    
    Format:
    
    北0 B-LOC
    京1 I-LOC
    欢0 O
    迎0 O
    你0 O

    Args:
        fp (str): The relative or absolute file path. 
        label_delimiter (str, optional): Default symbom of the delimiter. Defaults to "-".
        encoding (str, optional): The encoding of file. Defaults to "utf-8".

    Returns:
        Tuple[List,Set]: Return the sentence and the list of entity types within the boundary [l, r).
    """
    sentences, entity_type_set = read_conll(fp, label_delimiter, encoding)
    for i in range(len(sentences)):
        item = {
            "text":list(ch[:-1] for ch in sentences[i]["text"]),
            "entities":[]
        }
        for entity in sentences[i]["entities"]:
            item["entities"].append(entity)
            item["entities"][-1].update({
                "text": list(ch[:-1] for ch in entity["text"]),
            })
        sentences[i] = item
    return sentences, entity_type_set


def save_jsonl(fp: str, data: List[Any], encoding='utf-8'):
    """
    Save as jsonl file.

    Args:
        fp (str): The filename
        data (List[Any]): The list of data
    """
    dirname = os.path.dirname(fp)
    os.makedirs(dirname, exist_ok=True)
    with open(fp,"w", encoding=encoding) as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False))
            f.write('\n')
            f.flush()
            
def save_labels(fp: str, data: List[str], encoding='utf-8'):
    """
    Save labels as plaintext.

    Args:
        fp (str): The filename
        data (List[str]): Labels
        encoding (str, optional): The encoding of file. Defaults to 'utf-8'.
    """ 
    dirname = os.path.dirname(fp)
    os.makedirs(dirname, exist_ok=True)
    with open(fp, "w", encoding=encoding) as f:
        for item in data:
            f.write(item)
            f.write('\n')
            f.flush()

