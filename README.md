# Swarm Search — Project Handoff

*Last updated: June 2026*

## What this project is

A simulation of a drone swarm performing autonomous search over conflict-affected
terrain in Nigeria — specifically targeting two tasks:

1. **Hideout detection** — coverage search across large terrain (forests, hills,
   rural settlements) for structures or heat/RF signatures suggesting bandit
   camps.
2. **Victim/hostage localization** — once a zone of interest is flagged,
   narrowing down to precise location.

The motivating context is the banditry crisis in Nigeria's Northwest
(Zamfara, Katsina, Sokoto). This is a generalized-unit simulation — no
specific hardware platform is assumed. The goal right now is to get the
coordination algorithm right in simulation before any hardware
considerations enter the picture.

## Core idea: unified pheromone field

Instead of coordinating robots with a central controller or explicit
communication protocol, the swarm coordinates indirectly through a shared
**virtual pheromone field** — stigmergy, the same mechanism ants use.

The field is a scalar grid, each cell holding a value in **[-1, 1]**:

- **Negative** = repulsive — "this area is covered, go elsewhere"
- **Positive** = attractive — "something interesting here, investigate"
- **Zero** = neutral — unexplored

This single scale unifies what would otherwise be two separate systems
(coverage logic and detection logic) into one number a robot can read and
act on.

### Why two channels under the hood

Although robots act on a single net field value, the field is actually
computed from two separate channels that are tracked and decayed
independently:

- `F_cov` — coverage/repulsion, written whenever a robot passes through a
  cell, decays fast
- `F_det` — detection/attraction, written when a robot's sensor confidence
  crosses a threshold, decays slow

These are summed into `F_net = clip(F_cov + F_det, -1, 1)` for movement
decisions. The reason for keeping them separate rather than just using one
field: if you only had one number, a real detection signal sitting in a
heavily-searched (strongly repulsive) area could get mathematically
cancelled out and the swarm would ignore a genuine find. Mode-switching
logic checks `F_det` directly, not the net field, to avoid this.

### Field mechanics

- Both channels **evaporate toward zero** over time at different rates
  (`λ_cov` faster, `λ_det` slower) — this is what lets the swarm "forget"
  old coverage and allows revisiting areas, and also lets it stop chasing
  a detection that turns out to be stale.
- The field is **global and shared** — every robot reads and writes to the
  same grid. There is no per-robot local map; the grid itself is the
  swarm's collective memory.

## Robot behavior

Each robot has a **field of view (FOV)** radius. Movement logic:

1. Scan the field within FOV.
2. **If the FOV is entirely neutral** (no gradient to follow), the robot
   doubles its FOV radius and re-scans. This keeps repeating — the FOV
   keeps expanding — until either a gradient is found, or the FOV has
   grown to cover the entire shared grid. This was a deliberate choice to
   keep movement purposeful (gradient-seeking) rather than falling back to
   random walk in neutral territory.
3. Two modes:
   - **EXPLORE** — default mode, follows the gradient down toward neutral
     (away from repulsion), depositing coverage pheromone as it goes.
   - **CONVERGE** — triggered when `F_det` in FOV crosses an attraction
     threshold. Robot follows the `F_det` gradient upward toward the
     source.

## Distributed detection / quorum rule

A single robot's positive sensor reading does **not** count as a confirmed
detection — that would make the whole swarm vulnerable to one false
positive. A detection is only confirmed when **Q independent robots**
(currently planned: 3) report signal in the same region within a time
window. This is a distributed voting/quorum mechanism, deliberately chosen
over "first detection wins" given the humanitarian stakes of acting on a
wrong call.

## Current status

- **Design phase is done.** Full simulation plan is written (see
  `swarm_simulation_plan.md` if carried over, or recreate from this doc —
  the architecture, parameters, and build order are all specified there).
- **Code status: Pygame implementation already started.** Module
  architecture in progress:
  - `grid.py` — field state, read/write, decay
  - `robot.py` — robot state machine, FOV logic, sensor model
  - `swarm.py` — collection of robots, quorum accumulator
  - `simulation.py` — main loop, metric logging
  - `visualizer.py` — real-time rendering
  - `config.py` — centralized parameters
- Recommended build/test order: grid mechanics first (verify numerically
  before anything visual), then single robot behavior, then multi-robot,
  then sensor model, then quorum logic, then visualizer, then metrics.

## Key parameters (starting values — expect to tune)

| Parameter | Symbol | Initial value |
|---|---|---|
| Grid size | N | 100 × 100 |
| Number of drones | n | 20 |
| Base FOV radius | r_base | 5 cells |
| Max FOV radius | r_max | 70 cells |
| Coverage decay rate | λ_cov | 0.005 |
| Detection decay rate | λ_det | 0.001 |
| Coverage write strength | α_cov | 0.2 |
| Detection write strength | β_det | 0.3 |
| Neutral threshold | ε | 0.05 |
| Sensor detection threshold | θ_sense | 0.3 |
| Attraction follow threshold | θ_attract | 0.4 |
| Quorum count | Q | 3 |
| Quorum time window | T_window | 50 timesteps |
| Sensor noise std dev | σ | 0.15 |

## Test scenarios planned

- **Scenario A (sparse)** — few isolated targets, tests quorum/false
  positive suppression
- **Scenario B (clustered)** — targets grouped in one area, tests whether
  coverage repulsion correctly redirects the swarm after initial spread
- **Scenario C (adversarial)** — targets intermittently go quiet
  (simulating radio silence), tests whether detection decay rate allows
  re-detection without either losing track too fast or holding stale
  "ghost" detections too long

## Open questions / things to watch

- FOV expansion fallback: when max FOV is reached and the field is *still*
  neutral, robot moves to a random unvisited edge cell. "Unvisited" needs
  a precise definition (likely `|F_cov| < ε`) to avoid robots bouncing at
  grid boundaries.
- `λ_det` tuning is the most sensitive parameter — too fast and the swarm
  loses a target that goes quiet; too slow and false "ghost" detections
  linger and waste swarm resources.
- Metrics defined but not yet validated against real simulation runs:
  coverage rate, time to 90% coverage, redundancy ratio, true/false
  positive rate, time to first detection, and a combined weighted score.

## Why this design (in one paragraph, for context)

The whole point of stigmergic coordination is that no robot needs a map,
a leader, or global knowledge — intelligence emerges from local
interactions through the shared field. This matters specifically for
this application because conflict-zone deployments are exactly where
centralized control (single base station, hierarchical command structure)
is most fragile — it's a single point of failure and a jamming target.
A self-organizing, self-healing swarm where losing a unit just means
nearby pheromone repulsion fades and others drift in to cover the gap is
much more robust to the kind of adversarial, degraded-communication
environment this is actually meant to operate in.