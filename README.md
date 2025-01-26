# ups-monitoring

Monitor UPS battery module with Raspberry Pi

### How to:
1. Clone repo;
1. Creat a virtual environment and install required packages: `make deps-pi`;
1. Create a `systemd` file to auto start script on boot:

    ```
    # create file
    sudo touch /etc/systemd/system/ups-raspberrypi.service

    # edit file
    sudo vim /etc/systemd/system/ups-raspberrypi.service

    # add the content bellow:
    [Unit]
    Description=UPS Monitoring
    After=network.target

    [Service]
    Restart=on-failure
    User=pi
    WorkingDirectory=/home/pi/ups-raspberrypi
    ExecStart=/home/pi/ups-raspberrypi/.venv/bin/python3 ups_hat.py

    [Install]
    WantedBy=multi-user.target
    ```

1. Enable and start service:

    ```
    sudo systemctl enable ups-raspberrypi.service &&\
    sudo systemctl start ups-raspberrypi.service &&\
    sudo systemctl status ups-raspberrypi.service
    ```

1. Script will run on every 2 minutes, check logs inside `/home/pi/ups-raspberrypi/ups.log file`
