# Auto Entourage
Automatically populate an 3D environment with 2D entourage for visulization purposes.

## Sub-problem
1. height of the entourage (CV auto crop)
2. entourage population given a region, orientation, number, density
3. scaling entourage to match the 
4. automatically rotate entourage based on the camera angle

## Challenges
1. entourages might already be facing a particular angle, thus might not be appropriate to face the camera directly
2. lighting must match the global illumination in the model

## Moonshot
1. respond_to_challenge_1: what if entourage can be placed based on the best fitting angles. If we can extrapolate the orientation of the entourage, we might be able to place in accordance where they are best fit given a environmental region and a camera angle. Maybe we don't need to use object orientation detection but simply person skeleton mapping and extapolate from there.

2. vector entourage??
