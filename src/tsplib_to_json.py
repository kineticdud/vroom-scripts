#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, sys, math

# Generate a json-formatted problem from a tsplib file.

TSP_FIELDS = ['NAME',
              'TYPE',
              'COMMENT',
              'DIMENSION',
              'EDGE_WEIGHT_TYPE']

# Retrieve value for a one-liner TSPLIB entry.
def get_value(key, lines):
  result = None

  match = filter(lambda s: (s).startswith(key + ':'), lines)
  if len(match) > 0:
    result = match[0][len(key) + 1:].strip()
  else:
    # Also try with a space.
    match = filter(lambda s: (s).startswith(key + ' :'), lines)
    if len(match) > 0:
      result = match[0][len(key) + 2:].strip()

  return result

# TSPLIB canonic rounding.
def nint(x):
  return int(x + 0.5);

def euc_2D(c1, c2):
  xd = c1[0] - c2[0]
  yd = c1[1] - c2[1]
  return nint(math.sqrt(xd * xd + yd * yd))

# Compute matrix based on ordered list of coordinates.
def get_matrix(coords):
  matrix = []

  for i in range(len(coords)):
    line = []
    for j in range(len(coords)):
      # Should take symmetry into account to halve operations.
      line.append(euc_2D(coords[i], coords[j]))
    matrix.append(line)

  return matrix

def parse_tsp(input_file):
  with open(input_file, 'r') as file:
    lines = file.readlines()

  # Remember main fields describing the problem type.
  meta = {}
  for s in TSP_FIELDS:
    data = get_value(s, lines)
    if data:
      meta[s] = data

  # Only support EUC_2D for now.
  if ('EDGE_WEIGHT_TYPE' not in meta) or (meta['EDGE_WEIGHT_TYPE'] != 'EUC_2D'):
    print 'Unsupported EDGE_WEIGHT_TYPE.'
    exit(0)

  meta['DIMENSION'] = int(meta['DIMENSION'])

  # Find start of nodes descriptions.
  node_start = (i for i, s in enumerate(lines) if s.startswith('NODE_COORD_SECTION')).next()

  # Use first line as vehicle start/end.
  coord_line = lines[node_start + 1].strip().split(' ')

  coords = [[float(coord_line[1]), float(coord_line[2])]]

  vehicle = {
    'id': int(coord_line[0]),
    'start': [float(coord_line[1]), float(coord_line[2])],
    'start_index': 0,
    'end': [float(coord_line[1]), float(coord_line[2])],
    'end_index': 0
  }

  # Remaining lines are jobs.
  jobs = []

  for i in range(node_start + 2, node_start + 1 + meta['DIMENSION']):
    coord_line = lines[i].strip().split(' ')
    coords.append([float(coord_line[1]), float(coord_line[2])])
    jobs.append({
      'id': int(coord_line[0]),
      'location': [float(coord_line[1]), float(coord_line[2])],
      'location_index': i - node_start - 1
    })

  matrix = get_matrix(coords)

  return {'meta': meta, 'vehicles': [vehicle], 'jobs': jobs, 'matrix': matrix}

if __name__ == "__main__":
  input_file = sys.argv[1]
  output_name = input_file[:input_file.rfind('.tsp')] + '.json'

  pbl_instance = parse_tsp(input_file)

  with open(output_name, 'w') as out:
    print 'Writing problem ' + input_file + ' to ' + output_name
    json.dump(pbl_instance, out, indent = 2)

