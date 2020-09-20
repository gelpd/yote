# yote 🐴
<sub><sub>To yeet in past tense</sub></sub>

Organize and write structured machine learning logs and metrics *easily*

### Introduction
Solutions for organizing and storing metrics for machine learning experiments is a pain.
Existing solutions involve annoying setup instructions, dependence on infrastructural components,
and might be dependent on a machine learning framework choices.

Yote is built to integrate seamlessly with any code you write in python. It operates
locally by default, but gives you the flexibility to integrate metrics with services like Prometheus. 

### Usage
To use yote in your machine learning code to write metrics and logs, see the following example:

```
from yote import Experiment

experiment = Experiment()

while training:
    # doing work...
    experiment.emit({"loss": 0.3, "mse": 21})

```

You can 'load' up a previous experiment like so:
```
from yote import Experiment

experiment = Experiment.from_id("krabby-patty")

```

### Implementation

### Contributing

### TODO
 - cli explorer
 
