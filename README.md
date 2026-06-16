# Swarm Robotics Search Algorithm — Simulation Plan

## Overview

A multi-agent simulation of a drone swarm performing search operations over conflict-affected terrain. The swarm uses a unified pheromone-inspired weight field on a shared 2D grid to coordinate coverage and detection without any central controller.

---

## 1. World Representation

### The Grid
- A 2D discrete grid of cells, e.g. `N × N` (start with 100×100).
- Each cell `(i, j)` holds a **field value** `F[i][j] ∈ [-1.0, 1.0]`.
- Initial state: all cells set to `0.0` (unexplored / neutral).

### Cell States (by field value range)

| Range | Meaning |
|---|---|
| `F = 0.0` | Unexplored / neutral |
| `-1.0 ≤ F < 0.0` | Repulsive — recently covered, avoid |
| `0.0 < F ≤ 1.0` | Attractive — detection signal present, investigate |

The field is the swarm's **collective memory**. All robots read and write to the same grid.

---

## 2. Robot Model

### State Variables (per robot)
```
position:     (x, y)          # float coords, maps to grid cell
velocity:     (vx, vy)        # normalized direction vector
fov_radius:   r               # current field of view radius (cells)
fov_base:     r_base          # default FOV radius (e.g. 5 cells)
fov_max:      r_max           # max FOV radius (e.g. grid diagonal)
mode:         EXPLORE | CONVERGE
sensor_conf:  float ∈ [0, 1]  # confidence of current sensor reading
```

### Sensor Payload (simulated)
Each robot carries two simulated sensing channels:
- **Thermal IR** — detects heat signatures (camps, generators, bodies)
- **RF** — detects phone pings, radio emissions

In simulation, these are modelled as **ground truth signal fields** placed on the grid, with Gaussian noise added to each robot's reading.

---

## 3. The Pheromone Field

### Signal Types
Each robot broadcasts a typed signal:

```
signal = (value: float, source_type: "coverage" | "detection")
```

The grid stores a **net scalar field** used for movement, derived by summing contributions. But robots separately track decomposed channels to avoid suppressing real detections with coverage repulsion.

### Coverage Channel (repulsion)
When a robot moves through a cell, it writes:
```
F_cov[i][j] += -α_cov     # typically -0.2 per pass
```
This value decays toward 0 over time (evaporation):
```
F_cov[i][j] *= (1 - λ_cov)     # λ_cov ≈ 0.005 per timestep
```

### Detection Channel (attraction)
When a robot's sensor confidence crosses threshold `θ` in a cell:
```
F_det[i][j] += +β_det * sensor_conf    # e.g. +0.3 per timestep
```
This also decays, but more slowly (persistent signal):
```
F_det[i][j] *= (1 - λ_det)     # λ_det ≈ 0.001 per timestep
```

### Net Field (movement decision)
```
F_net[i][j] = clip(F_cov[i][j] + F_det[i][j], -1.0, 1.0)
```
Robots read `F_net` for movement but use the separate channels for mode switching logic.

---

## 4. Robot Behavior

### Movement Rules

**Step 1: Scan FOV**  
Robot reads `F_net` for all cells within radius `r` of its position.

**Step 2: FOV Expansion (if neutral)**  
If all cells in FOV have `|F_net| < ε` (ε ≈ 0.05):
- Expand `r` by step `Δr` (e.g. +3 cells)
- Repeat until gradient found OR `r = r_max` (full grid visibility)
- If `r_max` reached and still neutral → move to random unvisited edge cell

**Step 3: Mode Decision**  
- If `F_det` channel shows any cell in FOV with `F_det > θ_attract` (e.g. 0.4) → switch to `CONVERGE`
- Else → stay in `EXPLORE`

**Step 4: Movement**  
- `EXPLORE`: move in the direction of steepest *decrease* in `F_net` (away from repulsion, toward neutral)
- `CONVERGE`: move in the direction of steepest *increase* in `F_det` channel specifically

**Step 5: Write to Field**  
- Always write coverage repulsion to current cell
- If `sensor_conf > θ_sense` (e.g. 0.3) → write detection attraction

---

## 5. Distributed Detection (Quorum Rule)

A detection is **flagged as confirmed** only when:
- At least `Q` robots (e.g. 3) independently detect signal in the same grid region (within radius `r_confirm`)
- Within a time window `T_window` timesteps

This prevents a single noisy reading from triggering a mass false positive response.

**Implementation:**  
Each robot that detects something broadcasts: `(position, confidence, timestamp)` to the shared field. A lightweight confirmation accumulator counts independent contributions per region per time window.

---

## 6. Performance Metrics

### Coverage Efficiency
- **Coverage rate**: percentage of grid cells with `F_cov < -0.1` (visited) at each timestep
- **Time to 90% coverage**: primary coverage benchmark
- **Redundancy ratio**: average number of times each cell was visited (lower = more efficient)

### Detection Accuracy
- **True positive rate**: confirmed detections / total ground truth targets
- **False positive rate**: false confirmations / total confirmations
- **Time to first detection**: timesteps until first ground truth target confirmed

### Combined Metric
```
Score = w1 * (1 / T_90_coverage) + w2 * TPR - w3 * FPR
```
Where `w1, w2, w3` are tunable weights depending on mission priority (speed vs accuracy tradeoff).

---

## 7. Simulation Parameters (Initial Values)

| Parameter | Symbol | Initial Value |
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
| Detection sensor threshold | θ_sense | 0.3 |
| Attraction follow threshold | θ_attract | 0.4 |
| Quorum count | Q | 3 |
| Quorum time window | T_window | 50 timesteps |
| Sensor noise std dev | σ | 0.15 |

---

## 8. Ground Truth Targets (Test Scenarios)

### Scenario A — Sparse Targets
- 3 hideouts randomly placed, each with a Gaussian signal profile (σ=5 cells)
- 2 victim clusters, smaller signal radius (σ=2 cells)
- Designed to test: quorum rule, false positive suppression

### Scenario B — Clustered Targets
- Targets grouped in one quadrant
- Tests: whether coverage pheromone correctly redirects swarm after initial spread

### Scenario C — Adversarial
- Targets intermittently suppress their signal (simulating radio silence)
- Tests: detection decay allowing re-detection, swarm persistence

---

## 9. Implementation Stack

```
Language:     Python 3.x
Core loop:    NumPy (vectorized field operations)
Visualization: Matplotlib (real-time heatmap + robot positions)
              OR Pygame (for smoother animation)
Architecture: 
  - grid.py         # Field state, read/write, decay
  - robot.py        # Robot state machine, FOV logic, sensor model
  - swarm.py        # Collection of robots, quorum accumulator
  - simulation.py   # Main loop, metric logging
  - visualizer.py   # Real-time rendering
  - config.py       # All parameters in one place
```

---

## 10. Build Order

1. **Grid + field mechanics** — write/read/decay, verify numerically
2. **Single robot** — FOV scan, expansion, mode switching, movement
3. **Multi-robot** — shared field access, no inter-robot collision for now
4. **Sensor model** — ground truth signal + Gaussian noise
5. **Quorum accumulator** — confirmation logic
6. **Visualizer** — heatmap of F_net, robot positions, mode colors
7. **Metrics** — logging and plotting
8. **Scenario testing** — run A/B/C, tune parameters