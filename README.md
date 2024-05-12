# lineup
face database in browsers

## Aim

Puzzle pieces ask us to recognise from reference:
```mermaid
graph LR;
    A((10001 pieces left)) --> B[Blue Puzzle Piece]
    B -.-> C[Sky?]
    B -.-> D[Sea?]
```

```mermaid
graph LR;
    style E stroke-width:6px
    A((11 pieces left)) --> B[Green Puzzle Piece]
    B --> E["Tree on Left"]
```
We can reduce the time it takes to build up a whole series of references - we can offload that to a computer.

We can definitely do this for faces, as spoken about on the [Search Engine postcast](https://podcasts.apple.com/gb/podcast/should-this-creepy-search-engine-exist/id1614253637?i=1000655151849)

## Mechanism

Using Deepface to build up the reference list, an extension can allow for all faces recognised while browsing to be stored somewhere, then checked. 

This software decouples the browsing from the references.

Multiple people, on different browsers, can share the same database of references.

```mermaid
graph BT;
    B[firefox] --> A[face_database]
    C[librewolf] --> A
    D[firefox] --> A
    E[librewolf] --> A
    F[firefox] --> A
```
