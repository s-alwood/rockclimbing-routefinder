Rock climbing presents a uniquely complex pathfinding challenge because progress depends on coordinated limb movement, balance, reach, and constantly shifting body geometry. To explore how these factors can be modeled computationally, we developed a route‑finding system that generates human-like climbing sequences on indoor bouldering problems. Climbs are represented as graphs derived from manually collected hold‑quality assessments and image‑based measurements of hold size and position. A recursive search algorithm evaluates potential moves using a weighted quality function that incorporates hold strength, distance, biomechanical penalties, and simple movement heuristics. The system selects moves by examining short chains of future actions and choosing the path with the highest cumulative quality. Testing on real climbs showed that the algorithm reliably produced sequences that reached the designated top hold, but the resulting movement often felt rigid, occasionally overestimating reach or suggesting unstable limb configurations. These outcomes highlight both the promise and the limitations of simplified, limb‑based modeling. This work establishes a foundation for more advanced approaches that incorporate center‑of‑gravity estimation, dynamic movement patterns, richer hold geometry, and more nuanced representations of human climbing behavior.

Raw data/images are stored in all_data.csv and Images folder (images without _grid)
Processed data/images are stored in all_data_wc.csv and Images folder (images with _grid)

Run using testing.py
  if using your own raw data of form seen in all_data.csv

Run using runthrough.pt
  if using data provided here

Requires that the following are installed in the environment in which it is run:
- openCV
- matplotlib
- pandas
- numpy
