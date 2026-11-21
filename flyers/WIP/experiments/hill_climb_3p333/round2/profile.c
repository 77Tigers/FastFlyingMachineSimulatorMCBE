/* Minimum number of optional glue cells connecting required groups in a grid.
   Fixed face and pickup cells cost zero. An RB group contains its legal
   attachment neighbours, so the plate and connector can both pick up an RB. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* Every path from the root to this terminal group crosses the current
   boundary. Charging its unit cost once gives a lower bound even when the
   route branches, or several different pickups can serve one piston. */
static int cut_bound(int n, int groups, int cap, const int16_t *edges, const uint8_t *cost,
                     const int16_t *members, int reverse) {
  int root = 0;
  while (!(members[root] & 1) || cost[root])
    ++root;
  uint8_t residual[2048], seen[2048];
  int queue[2048], boundary[2048], bound = 0;
  memcpy(residual, cost, (size_t)n);
  for (int group = 0; group < groups; ++group) {
    int bit = 1 << (reverse ? groups - 1 - group : group);
    for (;;) {
      int tail = 0, nbound = 0;
      memset(seen, 0, n);
      for (int v = 0; v < n; ++v)
        if (members[v] & bit) {
          seen[v] = 1;
          if (residual[v])
            boundary[nbound++] = v;
          else
            queue[tail++] = v;
        }
      for (int i = 0; i < tail && !seen[root]; ++i)
        for (int d = 0; d < 6; ++d) {
          int w = edges[6 * queue[i] + d];
          if (w < 0 || seen[w])
            continue;
          seen[w] = 1;
          if (residual[w])
            boundary[nbound++] = w;
          else
            queue[tail++] = w;
        }
      if (seen[root])
        break;
      if (!nbound || ++bound > cap)
        return 0;
      for (int i = 0; i < nbound; ++i)
        residual[boundary[i]] = 0;
    }
  }
  return 1;
}

int profile(int n, int groups, int cap, const int16_t *edges, const uint8_t *cost,
            const int16_t *members, uint8_t *selected) {
  if (n <= 0 || n > 2048 || groups <= 0 || groups > 14 || cap < 0)
    return 100;
  for (int reverse = 0; reverse < 2; ++reverse)
    if (!cut_bound(n, groups, cap, edges, cost, members, reverse))
      return 100;
  int masks = 1 << groups;
  uint8_t *dist = malloc(n * masks);
  int *queue = malloc((n + 1) * sizeof(int));
  uint8_t *queued = calloc(n, 1);
  memset(dist, 100, n * masks);
  for (int mask = 1; mask < masks; ++mask) {
    uint8_t *row = dist + mask * n;
    if (!(mask & (mask - 1))) {
      for (int v = 0; v < n; ++v) {
        if (members[v] & mask) {
          row[v] = cost[v];
        }
      }
    }
    for (int part = (mask - 1) & mask; part; part = (part - 1) & mask) {
      int other = mask ^ part;
      if (other < part)
        continue;
      for (int v = 0; v < n; ++v) {
        int val = dist[part * n + v] + dist[other * n + v] - cost[v];
        if (val <= cap && val < row[v]) {
          row[v] = val;
        }
      }
    }
    int head = 0, tail = 0;
    for (int v = 0; v < n; ++v) {
      if (row[v] <= cap) {
        queue[tail++] = v;
        queued[v] = 1;
      }
    }
    while (head != tail) {
      int v = queue[head++];
      if (head == n + 1)
        head = 0;
      queued[v] = 0;
      for (int i = 0; i < 6; ++i) {
        int w = edges[6 * v + i];
        if (w < 0)
          continue;
        int val = row[v] + cost[w];
        if (val > cap || val >= row[w])
          continue;
        row[w] = val;
        if (!queued[w]) {
          queue[tail++] = w;
          if (tail == n + 1)
            tail = 0;
          queued[w] = 1;
        }
      }
    }
  }
  int full = masks - 1, best = -1;
  for (int v = 0; v < n; ++v) {
    if (dist[full * n + v] <= cap && (best < 0 || dist[full * n + v] < dist[full * n + best]))
      best = v;
  }
#ifdef RED_BRIDGE
  best = -1;
  for (int v = 0; v < n; ++v)
    if ((members[v] & 1) && dist[full * n + v] <= cap &&
        (best < 0 || dist[full * n + v] < dist[full * n + best]))
      best = v;
#endif
  int result = 100;
  if (best >= 0) {
    result = dist[full * n + best];
    for (int v = 0; v < n; ++v)
      selected[v] = dist[full * n + v];
  }
  free(dist);
  free(queue);
  free(queued);
  return result;
}
