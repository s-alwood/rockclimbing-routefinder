This repository contains all code, data, and final materials for **BetaQuest**, a rock-climbing route-finder. Please see "BetaQuest - Final Paper" for a detailed description of the project, development, and potential future addition. 
.
**Project description**
Rock climbing presents a uniquely complex pathfinding challenge because progress depends on coordinated limb movement, balance, reach, and constantly shifting body geometry. To explore how these factors can be modeled computationally, we developed a route‑finding system that generates human-like climbing sequences on indoor bouldering problems. Climbs are represented as graphs derived from manually collected hold‑quality assessments and image‑based measurements of hold size and position. A recursive search algorithm evaluates potential moves using a weighted quality function that incorporates hold strength, distance, biomechanical penalties, and simple movement heuristics. The system selects moves by examining short chains of future actions and choosing the path with the highest cumulative quality. Testing on real climbs showed that the algorithm reliably produced sequences that reached the designated top hold, but the resulting movement often felt rigid, occasionally overestimating reach or suggesting unstable limb configurations. These outcomes highlight both the promise and the limitations of simplified, limb‑based modeling. This work establishes a foundation for more advanced approaches that incorporate center‑of‑gravity estimation, dynamic movement patterns, richer hold geometry, and more nuanced representations of human climbing behavior.
.
**Descriptions of elements**
- Images folder: Both processed (with _grid suffix) and unprocessed (without _grid suffix) images used in development.
- "problem children" subfolder of "data stuff": images for climbs that caused issues with detection. Were not used in development.
- BetaQuest - Final Paper/Presentation/Poster: final products of the project, describe the process with varying levels of specificity.
- all_data.csv: unprocessed (manual) data
- all_data_wc.csv: processed (manual and image) data
- calibration_square.stl: design of image size reference square seen in the bottom right of all climb images.
- core_methods.py: contains move making, quality finding, move finding, and display methods.
- image_processing.py: contains image detection and processing methods
- preprocessing.py: contains manual/image data combination and graph creation methods
- qualitydata.csv: data about quality distributions, used for analysis
- recursive_attempts.py: contains final recursive route-finding method
.
Run using runthrough.py _if using data provided here_
Run using testing.py _if using your own raw data of form seen in all_data.csv_
.
Requires that the following are installed in the environment in which it is run:
- openCV
- matplotlib
- pandas
- numpy
