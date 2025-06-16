from collections import defaultdict
import math

# Constants
PROMOTE_AFTER = 30
MAX_DISTANCE = 150

# Global tracker
target_candidates = defaultdict(dict)

def update_target_candidates(ball_positions, all_targets):
    global target_candidates

    for color_name, coords in ball_positions.items():
        current_frame_hits = set()

        for (bx, by) in coords:
            found_similar = False

            for (cx, cy) in list(target_candidates[color_name].keys()):
                if math.hypot(bx - cx, by - cy) < MAX_DISTANCE:
                    target_candidates[color_name][(cx, cy)] += 1
                    current_frame_hits.add((cx, cy))
                    found_similar = True
                    break

            if not found_similar:
                target_candidates[color_name][(bx, by)] = 1
                current_frame_hits.add((bx, by))
        #if we want to delete targets after not being seen
        for pos in list(target_candidates[color_name].keys()):
            if pos not in current_frame_hits:
                target_candidates[color_name][pos] -= 1
                if target_candidates[color_name][pos] <= 0:
                    del target_candidates[color_name][pos]

        for pos, hits in list(target_candidates[color_name].items()):
            if hits >= PROMOTE_AFTER and pos not in all_targets:
                all_targets.append(pos)
                print(f"🎯 Promoted target {color_name} at {pos}")
                del target_candidates[color_name][pos]