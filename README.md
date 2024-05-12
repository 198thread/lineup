# lineup
face database when browsing

## Demo 


## Aim

Puzzle pieces ask us to recognise from reference:
```mermaid
graph LR;
    A(((10001/10001 pieces left))) --> B{{Blue Puzzle Piece}}
    B -.-> C([Sky?])
    B -.-> D([Sea?])
    B -.-> E([Blue petticoat?])
```

```mermaid
graph LR;
    A(((11 pieces left))) --> B{{Green Puzzle Piece}}
    B --> E[[Tree on Left]]
    A --> C{{Dark-Blue Puzzle Piece}}
    C --> D[[Sea]]
    A --> F{{Light-Blue Puzzle Piece}}
    F --> G[[Sky]]
```
We can reduce the Δtime it takes to build up a whole series of references, using machine learning.

We can definitely do this for faces, as PJ Vogt's [Search Engine postcast](https://podcasts.apple.com/gb/podcast/should-this-creepy-search-engine-exist/id1614253637?i=1000655151849) discusses

## Mechanism

Using Deepface to build up the reference list in Elasticsearch, a browser extension can allow for all faces recognised while browsing to be stored somewhere, then checked. 

This software decouples the browsing from the references.

Multiple people, on different browsers, can share the same database of references.

```mermaid
graph BT;
    B(firefox) <--> A[(face_db)]
    C{{librewolf}} <--> A
    D(firefox) <--> A
    E(firefox) <--> A
    F{{librewolf}} <--> A
```

## Installation

0. Install [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html#elasticsearch-install-packages)
1. Clone this repo
    2(Choice A). Add your Elasticsearch credentials into $cloned-repo/lineup-svr/env_dials.py
    2(Choice B). set *"xpack.security.enabled = False"* in elasticsearch/config
3. run *"pip install -r $cloned-repo/lineup-svr/requirements.txt"*
4.
    a. in your gecko-based browser (firefox/librewolf)
    b. go to about:debugging
    c. on the left select *"This Browser"*
    d. *"load temporary extension"*
    e. select *$cloned-repo/lineup-ext/manifest.json*

## License
Please observe the license, local laws - harmful action is ugly
