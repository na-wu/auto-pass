import random
import json
import sys

startingInt = sys.argv[0]


x = random.randint(1,101)

results = '{ "startingInt":startingInt, "randomInt":x}'



print(str(results))
sys.stdout.flush()
