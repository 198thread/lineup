# lineup
recognition of faces for the web

## Demo 

![lineup_demo](https://github.com/198thread/lineup/assets/169386773/74122711-ab81-41d0-83b0-44b1baeed941)


## Why

Puzzle pieces ask us to recognise from reference:

```mermaid
graph LR;
    A(((10001/10001 pieces left))) --> B([Blue Puzzle Piece])
    B -.-> C(Sky?)
    B -.-> D(Sea?)
    B -.-> E(Blue petticoat?)
```

```mermaid
graph LR;
    A(((11 pieces left))) --> B([Green Puzzle Piece])
    B --> E(Tree on Left)
    A ==> C([Dark-Blue Puzzle Piece])
    C --> D(Sea)
    A ==> F([Light-Blue Puzzle Piece])
    F --> G(Sky)
```
To reduce the Δtime it takes to build up references, machine learning libraries can be used.

As PJ Vogt's [Search Engine podcast](https://podcasts.apple.com/gb/podcast/should-this-creepy-search-engine-exist/id1614253637?i=1000655151849) discusses, this is possible for faces.

## Mechanism

Using face-recognition to build up the reference list in a database, the lineup browser extension can allow for all faces found while browsing to later be checked. 

This software uncouples the browsing and the reference list.

Multiple people, on different browsers, can share the same database of references.

```mermaid
graph BT;
    B(firefox) <--> A[(face_db)]
    C{{librewolf}} <--> A
    D(firefox) <--> A
    E(firefox) <--> A
    F{{librewolf}} <--> A
```

```mermaid
graph LR;
    A(((group's face_db))) --> B([face])
    B --> E(firefox)
    D{{librewolf}} --> C
    C([face]) --> A
    A --> F([face])
    F --> G(firefox)
    H(firefox) --> I([face])
    I --> A
```

# Installation Requirements & Usage

#### Requirements - Python & Database
1. Install [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html#elasticsearch-install-packages)
2. After installing elasticsearch: Edit *$elasticsearch-home/config/elasticsearch.yaml* and set  
   `xpack.security.enabled: false`

#### Installation - Client Side
1. Clone this repo
2. run `python3 -m pip install -r $repo/lineup_svr/requirements.txt`
  
## Usage
1. launch elasticsearch instance, wait until the output about 'health'
2. launch *$repo/lineup_svr/app.py* using `python3 app.py`
3. launch firefox, go to [about:debugging](about:debugging)
4. select `This Browser`, then `load temporary extension`
5. selecting *$repo/lineup_ext/manifest.json*

# Licensing

## Open Source License
This software is available under the [MIT License](LICENSE) for non-commercial use. This means individuals and organizations using the software without a commercial purpose can do so freely, with no cost, subject to the terms of the MIT License.

## Commercial use
This software is especially tailored to implement tracable security. A secure commercial version is also available.

Organisations wishing to use this software for commercial purposes should contact us to obtain a Commercial License.
