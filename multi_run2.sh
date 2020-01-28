problem="inc_or_dec"

mkdir "examples/simple/logs/$problem"

for i in {0..30}
do
  echo "Starting Run: $i"
  python examples/simple/$problem.py > examples/simple/logs/$problem/$i.txt
done

