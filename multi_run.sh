problem="vector-average"

mkdir "examples/software_synthesis/logs2/$problem"

for i in {0..30}
do
  echo "Starting Run: $i"
  time python examples/software_synthesis/run.py $problem > examples/software_synthesis/logs2/$problem/$i.txt
done
