for i in `seq 1 30`;
do
  echo $i
  nohup python3 examples/radio-speaker.py -f examples/config.json&
done
