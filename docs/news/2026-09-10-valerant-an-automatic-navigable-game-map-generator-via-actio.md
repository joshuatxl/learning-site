---
date: '2026-09-10'
fetched: '2026-09-10'
preview: World Action Models (WAMs) couple predictive world modeling with action generation,
  allowing anticipated future states to guide agent behavior. Although WAMs are rapidly
  advancing embodied AI, general-purpose counterparts remain largely unexplored in
  games…
published: '2026-09-10T04:00:00+00:00'
source: arXiv cs.AI
title: 'Valerant: An Automatic Navigable Game Map Generator via Action-Conditioned
  World Model Exploration'
url: https://arxiv.org/abs/2609.09418
---

# Valerant: An Automatic Navigable Game Map Generator via Action-Conditioned World Model Exploration

<p>World Action Models (WAMs) couple predictive world modeling with action generation, allowing anticipated future states to guide agent behavior. Although WAMs are rapidly advancing embodied AI, general-purpose counterparts remain largely unexplored in games. Existing game-oriented approaches often combine action-conditioned world models with external policies and reward functions to realize WAM-like decision-making, yet they operate mainly in 2D visual observation space and do not instantiate persistent 3D geometry. Extending this paradigm to 3D games introduces a distinct challenge. In autonomous driving and robotics, the physical environment exists independently of the model, providing a persistent 3D world in which selected actions can be executed. Games have no such external substrate; the virtual world itself must be instantiated. Most playable games require a persistent and navigable space, while 3D games additionally require explicit geometry that supports movement and interaction. Action-conditioned video rollouts provide visual observations but not this spatial representation. We present \textsc{Valerant}, a training-free framework that transforms a pretrained action-conditioned world model into a WAM for exploring and constructing 3D game maps. By coupling predictive visual rollouts with SLAM-based spatial reconstruction and exploration-driven action selection, \textsc{Valerant} progressively transforms a single image into a persistent 3D game map. This framework extends WAM-based interaction beyond 2D visual simulation and offers a new approach to reducing manual effort in 3D game-map creation.</p>

[Read the full article →](https://arxiv.org/abs/2609.09418)