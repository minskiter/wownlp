from typing import Dict, List, Tuple, Set, Union

from tqdm import tqdm

class LabelTokenizer():
    
    def __init__(self, filename: str=None) -> None:
        self.idx2label: List[str] = []
        self.label2idx: Dict[str, int] = {}
        if filename is not None:
            with open(filename, 'r') as f:
                for idx, line in tqdm(enumerate(f), desc=f'Loading labels from {filename}'):
                    self.idx2label.append(line.strip())
                    self.label2idx[line.strip()] = idx  
                    self.__make_o_first()
                    
    def __make_o_first(self):
        if "O" in self.label2idx:
            # find O idx
            idx = self.label2idx["O"]
            # swap with first label
            self.label2idx[self.idx2label[0]], self.label2idx["O"] = self.label2idx["O"], self.label2idx[self.idx2label[0]]
            self.idx2label[0],self.idx2label[idx] = self.idx2label[idx], self.idx2label[0]
                    
    def load(self, labels: List[str], sort=True):
        if sort:
            labels = list(labels)
            labels.sort()
        for label in labels:
            self.idx2label.append(label)
        for idx, label in enumerate(self.idx2label):
            self.label2idx[label] = idx
        self.__make_o_first()
        return self
    
    def remove(self, index: int):
        label = self.idx2label[index]
        self.idx2label.remove(label)
        self.label2idx = {}
        for idx, label in enumerate(self.idx2label):
            self.label2idx[label] = idx
        return self
    
    def add(self, item, index=-1):
        if index!=-1:
            self.idx2label.insert(index, item)
        else:
            self.idx2label.append(item)
        for idx, label in enumerate(self.idx2label):
            self.label2idx[label] = idx
        return self
    
    def convert_tokens_to_ids(self, label: Union[str, List[str]]) -> int:
        if isinstance(label, list):
            return [self.label2idx[l] for l in label]
        return self.label2idx[label]
    
    def convert_ids_to_tokens(self, idx: Union[int, List[int]]) -> int:
        if isinstance(idx, list):
            return [self.idx2label[i] for i in idx]
        return self.idx2label[idx]
    
    def __len__(self):
        return len(self.idx2label)
    
class HashTrie():
    
    def __init__(self) -> None:
        self.trie = set()
        self.max_length = 0
        
    def load_vocab_from_file(self, filename: str):
        with open(filename, 'r') as f:
            for line in tqdm(f, desc='Loading vocab'):
                self.trie.add(line.strip())
                self.max_length = max(self.max_length, len(line.strip()))
                
    def __add__(self, word):
        self.trie.add(word)
        self.max_length = max(self.max_length, len(word))
        return self
                
    def search_words(self, sentence: str, words_number:int=5, return_list=True):
        if return_list:
            words = []
        else:
            words = set()
        for start in range(len(sentence)):
            if return_list:
                words.append([])
            s = ""
            for end in range(start, min(start+self.max_length, len(sentence))):
                s += sentence[end]
                if s in self.trie:
                    if return_list:
                        words[-1].append(s)
                        if len(words[-1])>=words_number:
                            break
                    else:
                        words.add(s)
        return words
    
    def __len__(self):
        return len(self.trie)

def is_span_intersect(a: Tuple[int,int], b: Tuple[int,int]):
    """
    Determine if two spans intersect.
    a[0]<=b[1] and b[0]<=a[1]

    Args:
        a (Tuple[int,int]): First span
        b (Tuple[int,int]): Second span

    Returns:
        bool: True if intersect, otherwise False.
    """
    return a[0]<=b[1] and b[0]<=a[1]

def is_span_nested(a: Tuple[int,int], b: Tuple[int,int])->bool:
    """
    Determine if two spans nested.
    (b[0]<=a[0] and a[1]<=b[1]) or (a[0]<=b[0] and b[1]<=a[1])

    Args:
        a (Tuple[int,int]): First span
        b (Tuple[int,int]): Second span

    Returns:
        bool: True if nested, otherwise False.
    """
    return (b[0]<=a[0] and a[1]<=b[1]) or (a[0]<=b[0] and b[1]<=a[1])

def decode_sequence_labels(sequence: List[str], offset=0, delimiter="-"):
    """
    decode sequence labels.

    Args:
        sequence (List[str]): Labels sequence.
        offset (int, optional): The offset of start position. Defaults to 0.
        delimiter (str, optional): The delimiter of labels sequence. Defaults to "-".

    Raises:
        ValueError: Invalid labels

    Returns:
        entities (Set[Tuple[int, int, str]]): The set of entities. The range is [l,r].
    """
    entities = set()
    start = -1
    entity = None
    for end in range(len(sequence)):
        if sequence[end].startswith("B") or sequence[end].startswith("S"):
            if start>=0 and entity is not None:
                entities.add((start-offset, end-offset-1, entity))
            start = end
            entity = delimiter.join(sequence[end].split(delimiter)[1:])
        elif sequence[end].startswith("M") or sequence[end].startswith("I"):
            continue
        elif sequence[end].startswith("E"):
            if start>=0 and entity is not None:
                entities.add((start-offset, end-offset, entity))
            start = -1
            entity = None
        elif sequence[end].startswith("O"):
            if start>=0 and entity is not None:
                entities.add((start-offset, end-offset-1, entity))
            start = -1
            entity = None
        else:
            raise ValueError(f"Invalid label {sequence[end]}")
    if start>=0 and entity is not None:
        entities.add((start-offset, len(sequence)-offset-1, entity))
    return entities