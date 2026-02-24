# Deep-CFR-for-HUNLHE
A Deep CFR poker bot for heads-up no-limit Texas Hold'em.

Based on Noam Brown's Deep CFR architecture with changes made to the network structure.
Game engine with inbuilt betting abstraction and efficient state encoding from scratch (~75k randomly sampled hand rollouts per second)

engine.py contains all of the game logic and encodes states as a tuple. The main logic controlled by the "proceed" method takes a state vector and an action, and returns the new state vector or payoffs if the hand is done. phevaluator used for high speed hand evaluation using a perfect hashing algorithm. Includes "test_speed" method for testing simulation speed. Configurable game parameters (blinds, stacks, etc) contained within global variables at the start of the file. 
