# Diagram types

One section per type: architecture, sequence, state, entity-relationship, flowchart, swimlane, deployment, dependency, timeline, layers. Visual rules: [style.md](style.md). Connectors: [connectors-and-icons.md](connectors-and-icons.md). Check before reporting: `python3 assets/diagram/check.py out.svg`.

## Architecture

**The reader asks:** What are the parts, and who talks to whom?

Boxes grouped by what they share: a process, a host, a repository, a trust boundary. Each group is a `zone`; a part outside every zone is external (a client, a third-party API).

- Builder: nodes in one or two rows, one zone per group, `main` connectors for the request path, `secondary` for the rest, `optional` for retry and build-time links. Example: `assets/diagram/examples/service-request.json`.
- One part feeding several (a router, a queue to its consumers): put the targets in a column and use the `z` route with `slot` ([../connectors-and-icons.md](connectors-and-icons.md)); example `assets/diagram/examples/fan-out.json`.
- Budget: 9 nodes, 12 connections, one or two focal nodes (the part the reader came to understand).
- Name the node by what it is (`Queue`) and its role by what it runs (`redis list`). Ports and paths go in mono (`"mono": true`).
- Every part and arrow must be real: one you cannot point to in the code is marked as assumed or left out.
- Past 9 nodes: an overview with one zone per subsystem, then one picture per subsystem.

## Dependency graph

**The reader asks:** What depends on what?

Use it when fan-in or a cycle makes a tree wrong. Direction is "depends on": the arrow points at the dependency.

- Builder: put the most depended-on node at the right or bottom, the entry points at the left or top, so arrows run one way. A cycle is drawn as one `optional` connector back, with the label `CYCLE`; it is the finding, so make it the focal edge's neighbour.
- Group by package with zones when there are more than 9 modules, and show one picture per package.
- A picture of every import in a project is a hairball. Draw the modules the question is about and their direct neighbours only.

## Deployment

**The reader asks:** Where does it run?

Zones for hosts, regions or clusters; nodes for the artifacts that run there (a container, a process, a function); connectors for the traffic between them. Ports, image names and paths are technical values and go in mono.

- Builder: one zone per boundary, nested one level at most (a region holding two hosts), `"mono": true` on nodes whose role is a port or image (`:8000`, `api:1.4`).
- Show replicas as a count in the role (`3 replicas`), not as three identical boxes.
- Mark what is public: the edge from outside the outermost zone is the `main` connector.
- Budget: 9 nodes. Show what you can point to in the repository (a Dockerfile, a compose file, a manifest); anything else is marked assumed.

## Entity-relationship

**The reader asks:** What does the data look like, and how do the tables relate?

A table node per entity: its name, then one mono row per column that matters (key, foreign key, a column the reader needs), with the type at the right. A connector per relationship, labelled with its cardinality (`1 : N`).

- Builder: `rows: [["id","uuid"],["user_id","uuid"]]` makes a table node. Example: `assets/diagram/examples/shop-tables.json`.
- Show columns that carry meaning (keys, status, the columns a query filters on), not every column; say so in the subtitle when you leave some out.
- Connectors run from the foreign key's table to the referenced one in the direction a reader says it (`users` to `orders` for "one user places many orders").
- Budget: 6 tables. A schema of 20 tables is a set of pictures, one per aggregate.
- Physical detail (indexes, constraints) belongs in the migration, not in the picture.

## Flowchart

**The reader asks:** What are the steps, and where does it branch?

Steps in reading order, left to right or top to bottom, with a question node wherever the path splits. Use it for logic with real branches; a linear list of steps is a numbered list.

- Builder: a step is a node with an action icon; a decision is a node named as a question (`Retries left?`) with icon `git-fork` or `help`. Its two exits are labelled `YES` and `NO`, one `main` (the common path) and one `secondary`.
- Rejoin branches so the picture ends in one place; a dead end is a terminal node that says why (`Dropped`).
- Budget: 9 nodes. Two decisions in a row usually mean a table of cases is clearer.
- When who does each step matters, use the swimlane section below instead.

## Layer stack

**The reader asks:** What sits on what?

Stacked abstraction levels, each a band that depends only on the one below it (application over library over runtime over operating system).

- Builder: one `zone` per layer, stacked, labelled; two or three nodes inside each; `v` connectors only where a layer calls the next. A connector that skips a layer is the finding.
- Order: the layer users touch on top.
- Budget: 5 layers, 9 nodes. If everything calls everything, it is not layered, and a dependency graph is the honest picture.

## Sequence

**The reader asks:** In what order do things happen between parts?

One column per participant, time running down, a horizontal arrow per message. The builder does not draw lifelines: draw it by hand with the contract in [../style.md](style.md), the same tokens and the same pill labels.

- Header: each participant is a node-style box in a row at the top; a dashed `line`-colour lifeline drops from it.
- Messages: a solid arrow for a call, a dashed arrow for a return. The label names the call (`POST /orders`), above the arrow, on a pill if it crosses a lifeline.
- Activation: a narrow `accent-tint` bar on the lifeline while a participant works. At most one focal message.
- Budget: 5 participants, 12 messages. Past that, split by phase (a happy path and a failure path are two pictures).
- Alternatives (`alt`, `loop`) are a labelled `zone` behind the messages they wrap; more than one nesting level means the flow belongs in a flowchart or in prose.

## State machine

**The reader asks:** What states can one thing be in, and what moves it?

A node per state, a connector per transition, labelled with the event that causes it. The start is where the reader looks first; terminal states say so in their role (`closed`).

- Builder: states in one row along the happy path (`main` connectors), exits and error states below it (`optional`, routes `vh`, `below`). Example: `assets/diagram/examples/order-states.json`.
- Focal: the state where the interesting work happens, not the first one.
- A guard goes in the label (`PAID`, `NO STOCK`), never in a second line of small text.
- Budget: 9 states, 12 transitions. A state with transitions to every other state is a flag in disguise; merge or split it.
- Every state and event comes from the code or the user; one you cannot point to is marked as assumed.

## Swimlane

**The reader asks:** Who does each step, and where does work change hands?

One horizontal band per actor (a person, a team, a service), steps inside their owner's band, connectors crossing bands where work is handed over.

- Builder: one `zone` per lane, full width and stacked, labelled with the actor; nodes inside; connectors between lanes use `vh` or `v`. A handoff is the connector worth labelling.
- Lane order follows the flow: the actor who starts is on top.
- Budget: 4 lanes, 9 steps. More lanes usually mean two processes.

## Timeline

**The reader asks:** When did or will things happen, and in what order?

Events in one row, in time order, each with its date in the role line. Equal spacing means order only; if the gaps carry meaning (a year of nothing), say so in the subtitle or space the nodes to scale.

- Builder: nodes in one row joined by `secondary` connectors, no labels; the focal node is the event the reader should remember. Mark a future event with an `optional` connector into it.
- Budget: 9 events. Two timelines compared are two rows with the same scale.
- A date list with nothing to say about the gaps is a table.

