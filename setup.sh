#!/bin/bash
python_path=$(which python3)
current_path=$(pwd)

echo "Replacing Python Path and Working diretory in service file"
echo $python_path
echo $current_path

sed -i "s@WorkingDirectory=.*@WorkingDirectory=$current_path@g" thm-grade-grabber.service
sed -i "s@ExecStart=.*@ExecStart=$python_path $current_path/grab.py \&@g" thm-grade-grabber.service

sudo cp thm-grade-grabber.service /etc/systemd/system/
sudo systemctl enable thm-grade-grabber.service
sudo systemctl start thm-grade-grabber.service

